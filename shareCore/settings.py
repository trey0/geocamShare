
STATUS_CHOICES = (('p', 'pending'), # in db but not fully processed yet
                  ('a', 'active'),  # active, display this to user
                  ('d', 'deleted'), # deleted but not purged yet
                  )
# define constants like STATUS_PENDING based on above choices
for code, label in STATUS_CHOICES:
    globals()['STATUS_' + label.upper()] = code

GALLERY_PAGE_COLS = 3
GALLERY_PAGE_ROWS = 4

GALLERY_THUMB_SIZE = [160, 120]
DESC_THUMB_SIZE = [480, 360]
