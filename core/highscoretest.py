import random
import string
import sys
import unittest

import highscoretable

TABLE_SIZE = 10
MODE       = random.choice(xrange(1, 6))

class HighScoreTest(unittest.TestCase):
    scores = highscoretable.HighScoreTable("scores.cg", MODE, TABLE_SIZE, "Scores", 'n')
    
    def setUp(self):
        print "Start test!"

    def test_01_add_scores(self):
        for i in xrange(TABLE_SIZE):
            self.scores.addScore(
                HighScoreTable.HighScoreEntry(random.choice(string.ascii_letters),
                               random.choice(xrange(0, 100000000, 100)),
                               MODE
                               )
                )
            
        self.assertEqual(TABLE_SIZE,
                         len(self.scores),
                         "The score entries were not added successfully!  The score table size does not hold the same amount oentries as its length!"
                         )
        print "Added scores successfully!"

    def test_02_get_scores(self):
        a = self.scores.getScores()
        for i in a: print i
        self.assertTrue(isinstance(a, list), "HighScoreTable.getScores() returns a " + type(a).__name__ + "instead of a list.")
        self.assertEqual(len(a), TABLE_SIZE)

        print "Retreived scores successfully!"

    def test_03_close(self):
        self.scores.scorefile.close()
        print "File closed successfully!  All done!"


if __name__ == "__main__":
    reload(HighScoreTable)

    suite = unittest.TestLoader().loadTestsFromTestCase(HighScoreTest)
    unittest.TextTestRunner(verbosity = 2).run(suite)

    print "Done testing."