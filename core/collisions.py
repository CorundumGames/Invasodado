import itertools

import pygame.sprite
import pygame.time

from game import block
from game import shipbullet
from game import enemy
import config
import gsm

do_not_compare = {(block.Block          , shipbullet.ShipBullet),
                  (shipbullet.ShipBullet, block.Block          ),
                  (block.Block          , enemy.Enemy          ),
                  (enemy.Enemy          , block.Block          )
                  }

do_not_check = {block.Block, pygame.sprite.Sprite}

class CollisionGrid:
    '''CollisionGrid is a grid meant to be used to easily determine whether or
    not objects within are colliding; only objects within the same cell are
    compared against each other.
    '''
    def __init__(self, width, height, layer):
        '''width and height are how big we want the grid to be in *cells*, not
        in pixels!'''
        cell_width            = config.screen.get_width()/width
        cell_height           = config.screen.get_height()/height
        
        self.collisions       = []
        self.grid             = [[GridCell(pygame.Rect(i*cell_width ,
                                                       j*cell_height,
                                                       cell_width   , 
                                                       cell_height
                                                       ),
                                           self) 
                                  for i in range(width)]
                                  for j in range(height)
                                  ]
        self.layer            = layer
        self.spare_collisions = []
    
    def update(self):
        '''Removes objects no longer in this cell, and adds ones that just
        entered.  Called every frame.'''
        for row in self.grid:
        #For all rows in this grid...
            for cell in row:
            #For all cells in this row...
                cell.remove_exiting()
                cell.add_entering()
                cell.check_collisions()
                
        self.handle_collisions()
                
    def handle_collisions(self):
        '''Handles all collisions, from first to last.'''
        self.collisions.sort()
        for i in self.collisions:
        #For all collisions
            i.obj1.on_collide(i.obj2)
            i.obj2.on_collide(i.obj1)
            i.reset()
            
        self.spare_collisions += self.collisions
        del self.collisions[:]
        
        
################################################################################

class GridCell:
    '''GridCell is meant to be held by a CollisionGrid.  It contains the set of
    all objects within its assigned area.  This way, only objects in the same
    cell are checked for collisions.
    '''
    def __init__(self, rect, grid):
        '''grid is the CollisionGrid that holds this GridCell.
           objects is the set of all objects in this cell.
           objects_to_add is the set of all objects that just entered this cell.
           objects_to_remove is the set of all objects that just left this cell.
           rect is the rectangular area that this cell occupies.
        '''
        self.grid              = grid
        self.objects           = set()
        self.objects_to_add    = set()
        self.objects_to_remove = set()
        self.rect              = rect

    def remove_exiting(self):
        '''Removes objects that are no longer within this cell.'''
        for o in self.objects:
        #For all objects in this cell...
            if not self.rect.colliderect(o.rect):
            #If this object is no longer in this cell...
                self.objects_to_remove.add(o)
                
        self.objects -= self.objects_to_remove
        self.objects_to_remove.clear()

    def add_entering(self):
        '''Adds objects that are held within this cell.'''
        for g in gsm.current_state.group_list:
        #For all groups on-screen...
            for s in itertools.ifilter(lambda x: type(x) not in do_not_check, g):
            #For all sprites in this group...
                if s not in self.objects and self.rect.colliderect(s.rect):
                #If the sprite is not already in this cell...
                    self.objects_to_add.add(s)
                    
        self.objects |= self.objects_to_add
        self.objects_to_add.clear()
                    
    def check_collisions(self):
        '''Sees if any objects collide, preps them to be handled if so.'''
        grid = self.grid
        
        for i, j in itertools.combinations(self.objects, 2):
        #For all possible combinations of objects that can touch...
            if pygame.sprite.collide_rect(i, j) or \
            i.rect.move(i.velocity[0], i.velocity[1]).colliderect(j.rect.move(j.velocity[0], j.velocity[1])):
            #If these two objects touch or if they're about to touch...
                if len(grid.spare_collisions) == 0:
                #If we don't have any spare Collision objects...
                    grid.spare_collisions.append(Collision())
                grid.collisions.append(grid.spare_collisions.pop().update(i, j))
                 
                 
################################################################################           
                    
class Collision:
    '''Collision is a convenient way to store data about...collisions.
    
    These should be part of a list with an initial amount of Collisions.  If
    more are needed, add them.
    
    Do not create these on the fly!  Recycle them often with self.update()!
    Then when the collision is handled, call self.reset().
    '''
    def __init__(self):
        self.obj1 = None
        self.obj2 = None
        self.time = None
        
    def update(self, obj1, obj2):
        '''Lets this Collision object know which two entities have collided, and
        record the time that it happened.'''
        self.obj1, self.obj2 = obj1, obj2
        self.time = pygame.time.get_ticks()
        return self
        
    def reset(self):
        '''Clears this Collision's fields (so we don't need to delete this
        and create another).'''
        self.obj1 = None
        self.obj2 = None
        self.time = None
        return self
        
    def __cmp__(self, other):
        '''Lets us sort Collisions by time.'''
        return cmp(self.time, other.time)