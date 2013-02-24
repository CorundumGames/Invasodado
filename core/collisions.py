'''
This module is a system for collision between Axis-Aligned Bounding Boxes.
It's meant to be reused in other games, so I tried to keep this as general as
possible.

@var _do_not_check: Game object types that don't collide (for performance)
@var _do_not_compare: Object type pairings that don't collide with each other
'''

from itertools import chain, combinations, filterfalse

import pygame.display
import pygame.sprite
import pygame.time

### Globals ####################################################################
_do_not_compare = set()
#Contains 2-tuples of types.  Don't check for collisions between objects
#with these type pairings.

_do_not_check   = set()
################################################################################

### Functions ##################################################################
def dont_check_type(*types):
    '''
    Prevents the given types of objects from colliding with other objects.

    @param types: Arbitrary number of types not to check for collisions.
    @postcondition: The classes in types are no longer capable of collisions.
    '''
    _do_not_check.update(types)
################################################################################

class CollisionGrid:
    '''
    CollisionGrid is a grid meant to be used to easily determine whether or
    not objects within are colliding; only objects within the same cell are
    compared against each other.
    
    CollisionsGrids themselves are not aware of the space they take up on-screen,
    that's the job of the GridCells they hold.
    '''
    def __init__(self, width, height, layer, group_list):
        '''
        @param width: Width of this CollisionGrid in cells
        @param height: Height of this CollisionGrid, also in cells
        @param layer: Only objects whose layer attribute == self.layer can touch
        @param group_list: List of all Pygame groups to check for collisions in
        
        @ivar collisions: List of all collisions that occurred in the last frame
        @ivar grid: The cells of this grid
        @ivar group_list: List of all Pygame groups to check for collisions in
        @ivar layer: Only objects of the same layer may collide
        @ivar spare_collisions: Spare Collisions, so we don't keep creating them
        '''
        size = pygame.display.get_surface().get_size()
        cell_size = (size[0] / width, size[1] / height)
        
        def get_pos(i, j):
            return (i*cell_size[0], j*cell_size[1])

        self.collisions = []
        self.grid       = [[GridCell(pygame.Rect(get_pos(i, j), cell_size), self)
                                    for i in range(width)
                            ]
                            for j in range(height)
                          ]
        self.group_list = group_list
        self.layer      = layer
        self.spare_collisions = []

    def update(self):
        '''
        Removes objects no longer in this cell, and adds ones that just
        entered.  Called every frame.
        '''
        for i in chain.from_iterable(self.grid):
            i.remove_exiting()
            i.add_entering()
            i.check_collisions()

        self.handle_collisions()

    def handle_collisions(self):
        '''
        Handles all collisions, from first to last.
        '''
        collisions = self.collisions
        collisions.sort()

        for i in collisions:
        #For all collisions that have occurred...
            i.obj1.on_collide(i.obj2)
            i.obj2.on_collide(i.obj1)
            i.reset()

        self.spare_collisions += collisions
        del collisions[:]


################################################################################

class GridCell:
    '''
    GridCell is meant to be held by a CollisionGrid.  It contains the set of
    all objects within its assigned area.  This way, only objects in the same
    cell are checked for collisions.
    '''
    def __init__(self, rect, grid):
        '''
        @ivar grid: The CollisionGrid to report Collisions to
        @ivar objects: Objects that this GridCell will check for collisions
        @ivar objects_to_add: Objects that are entering this GridCell's rect
        @ivar objects_to_remove: Objects that are leaving this GridCell's rect
        @ivar rect: Rectangular area to check for collisions in
        '''

        self.grid              = grid
        self.objects           = set()
        self.objects_to_add    = set()
        self.objects_to_remove = set()
        self.rect              = rect

    def remove_exiting(self):
        '''
        Removes objects that are no longer within this cell.
        '''
        objects_to_remove = self.objects_to_remove

        for i in filterfalse(self.rect.colliderect, self.objects):
            objects_to_remove.add(i)

        self.objects -= objects_to_remove
        objects_to_remove.clear()

    def add_entering(self):  #TODO: Optimize!
        '''
        Adds objects to this cell if they enter.
        '''
        objects_to_add = self.objects_to_add
        rect           = self.rect

        for i in (j for j in chain.from_iterable(self.grid.group_list)
                  if j.__class__ not in _do_not_check
                  and j.rect.colliderect(rect)):
        #For all sprites in this group that aren't excluded from collisions
        #and have just entered this cell...
            objects_to_add.add(i)

        self.objects |= objects_to_add
        objects_to_add.clear()

    def check_collisions(self):
        '''
        Sees if any objects collide, preps them to be handled if so.
        '''
        grid = self.grid

        for i, j in combinations(self.objects, 2):
        #For all possible combinations of objects that can touch...
            if pygame.sprite.collide_rect(i, j):
            #If these two objects touch...
                if not grid.spare_collisions:
                #If we don't have any spare Collision objects...
                    grid.spare_collisions.append(Collision())
                grid.collisions.append(grid.spare_collisions.pop().update(i, j))


################################################################################

class Collision:
    '''
    Collision is a convenient way to store data about...collisions.

    These should be part of a list with an initial amount of Collisions.  If
    more are needed, add them.

    Do not create these on the fly!  Recycle them often with self.update()!
    Then when the collision is handled, call self.reset().

    Reason is, creating new objects is expensive.  Reusing them isn't.
    '''
    def __init__(self):
        '''
        @ivar obj1, obj2: The two objects involved in this collision
        @ivar time: The time this collision happened (system time, of course)
        '''
        self.obj1  = None
        self.obj2  = None
        self._time = None

    def update(self, obj1, obj2):
        '''
        Lets this Collision object know which two entities have collided, and
        record the time that it happened.
        
        @param obj1, obj2: The two objects that just collided
        @return: self
        '''
        self.obj1, self.obj2 = obj1, obj2
        self._time           = pygame.time.get_ticks()
        return self

    def reset(self):
        '''
        Clears this Collision's fields (so we don't need to delete this and
        create another).
        
        @postcondition: This Collision's fields are all None
        @return: self
        '''
        self.obj1, self.obj2, self._time = None, None, None
        return self

    def __lt__(self, other):
        '''
        Lets us sort Collisions by time.
        
        @param other: The other Collision being compared with this one
        '''
        return self._time < other._time