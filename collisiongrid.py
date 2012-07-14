import pygame
import config
import gsm

class CollisionGrid:
    '''CollisionGrid is a grid meant to be used to easily determine whether or
    not objects within are colliding; only objects within the same cell are
    compared against each other.
    '''
    def __init__(self, width, height):
        '''width and height are how big we want the grid to be in *cells*, not
        in pixels!'''
        cell_width = config.screen.get_width()/width
        cell_height = config.screen.get_height()/height
        
        self.grid = [[GridCell(pygame.Rect(i*cell_width,
                                           i*cell_height,
                                           cell_width,
                                           cell_height
                                           ))
                      for i in range(width)] for j in range(height)]
        self
    
    def update(self):
        '''Removes objects no longer in this cell, and adds ones that just
        entered.  Called every frame.'''
        for row in self.grid:
            for cell in row:
                cell.remove_exiting()
                cell.add_entering()
                
    def handle_collisions(self):
        pass



class GridCell:
    def __init__(self, therect):
        self.rect = therect
        self.objects = set()
        self.objects_to_add = set()
        self.objects_to_remove = set()

    def remove_exiting(self):
        '''Removes objects that are no longer within this cell.'''
        for o in self.objects:
            if not self.rect.colliderect(o.rect):
                self.objects_to_remove.add(o)
                
        self.objects -= self.objects_to_remove
        self.objects_to_remove.clear()

    def add_entering(self):
        '''Adds objects that are held within this cell.'''
        for g in gsm.current_state.group_list:
            for s in g:
                if self.rect.colliderect(s.rect) and s not in self.objects:
                    self.objects_to_add.add(s)
                    
        self.objects |= self.objects_to_add
        self.objects_to_add.clear()
                    
    def check_collisions(self):
        pass
        