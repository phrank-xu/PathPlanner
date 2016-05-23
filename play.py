#!/usr/local/bin/python

import heapq as pq, numpy as np, operator, unittest

BOARD8 = "........ ........ ........ ........ ........ ........ ........ ........".split()
BOARD32 = "........B...LLL................. ........B...LLL................. ........B...LLL...LLL........... ........B...LLL..LLL...RR....... ........B...LLLLLLLL...RR....... ........B...LLLLLL.............. ........B............RR......... ........BB...........RR......... ........WBB..................... ...RR...WWBBBBBBBBBB............ ...RR...WW.........B............ ........WW.........B......T..... ...WWWWWWW.........B............ ...WWWWWWW.........B..RR........ ...WW..........BBBBB..RR.WWWWWWW ...WW..........B.........W...... WWWW...........B...WWWWWWW...... ...WWWWWWW.....B............BBBB ...WWWWWWW.....BBB..........B... ...WWWWWWW.......BWWWWWWBBBBB... ...WWWWWWW.......BWWWWWWB....... ...........BBB..........BB...... .....RR....B.............B...... .....RR....B.............B.T.... ...........B.....RR......B...... ...........B.....RR............. ...........B..........RR........ ...........B..........RR........ ...........B.....RR............. ...........B.....RR............. ...........B.....RR............. ...........B.....RR.............".split()
NEXT = [(1, 2), (2, 1), (-1, 2), (2, -1), (1, -2), (-2, 1), (-1, -2), (-2, -1)]
MOVE_MAP = {'T': 1, 'W': 2, 'L': 5, '.': 1}

def okPosition(board, position): 
    x, y = position
    return x >= 0 and x < len(board[0]) and y >= 0 and y < len(board) and board[y][x] != 'R' and board[y][x] != 'B'

def okMove(board, src, dst):
    x_src, y_src = src
    x_dst, y_dst = dst
    def okL(): 
        dx, dy = abs(x_src - x_dst), abs(y_src - y_dst)
        return dx > 0 and dy > 0 and (dx + dy) == 3
    # Barrier
    def okB():
        dx, dy = x_dst - x_src, y_dst - y_src
        sx, sy = np.sign([dx, dy])
        ox, oy = dx - sx, dy - sy
        return board[y_src+sy][x_src+sx] != 'B' and board[y_src+oy][x_src+ox] != 'B'
    # Teleport
    def okT():
        return board[y_src][x_src] == 'T' and board[y_dst][x_dst] == 'T'
    return okT() or okL() and okB()

def okTransport(board, src, dst, base):
    return base != None and okMove(board, src, base) and board[base[1]][base[0]] == 'T' and board[dst[1]][dst[0]] == 'T'
    
def printBoard(board):
    for i in xrange(len(board)):
        print '    ' + board[i]
    print "\n"

def printBoardWithMoves(board, moves):
    current = [r[:] for r in board]
    for i in xrange(len(moves)):
        x, y = moves[i]
        current[y] = current[y][:x] + '%d' % i + current[y][x+1:]
    printBoard(current)
    
def validate(board, moves):
    def printBoardWithPosition(move):
        current = [r[:] for r in board]
        x, y = move
        current[y] = current[y][:x] + 'K' + current[y][x+1:]
        printBoard(current)

    if not okPosition(board, moves[0]):
        return False
    for i in xrange(1, len(moves)):
        if not okPosition(board, moves[i]) or not okMove(board, moves[i-1], moves[i]):
            return False
    print 'movement: '
    for i in range(len(moves)):
        print '  move %d: ' % i
        printBoardWithPosition(moves[i])
    return True

def compute(board, src, dst):
    if not okPosition(board, src) or not okPosition(board, dst):
        return []
    Ts, t_base = set((x, y) for y, row in enumerate(board) for x, c in enumerate(row) if c == 'T'), None
    queue, visited = [src], {}
    visited[src] = src  
    while queue:
        for n in NEXT:
            next = tuple(map(operator.add, queue[0], n))
            if next not in visited and okPosition(board, next) and (okMove(board, queue[0], next) or okTransport(board, queue[0], next, t_base)):
                visited[next] = queue[0]
                queue.append(next)
                if next in Ts:
                    t_base = next
                    for t in Ts:
                        if t != next:
                            visited[t] = next
                            queue.append(t)
                else:
                    visited[next] = queue[0]
                    queue.append(next)
                if next == dst:
                    moves = [dst]
                    while moves[0] != src:
                        moves.insert(0, visited[moves[0]])
                        if moves[0] in Ts:
                            moves.insert(0, t_base)
                    printBoardWithMoves(board, moves)
                    return moves
        queue.pop(0)
    return []

def shortest(board, src, dst):
    if not okPosition(board, src) or not okPosition(board, dst):
        return []
    Ts, t_base = set((x, y) for y, row in enumerate(board) for x, c in enumerate(row) if c == 'T'), None
    # print 'Ts: ', Ts
    queue, visited = [(0, src)], {}
    visited[src] = src  
    while queue:
        d_last, p_last = pq.heappop(queue)
        for n in NEXT:
            p_next = tuple(map(operator.add, p_last, n))
            if p_next not in visited and okPosition(board, p_next) and (okMove(board, p_last, p_next) or okTransport(board, p_last, p_next, t_base)):
                x, y = p_next
                d_next = d_last + MOVE_MAP[board[y][x]]
                visited[p_next] = p_last
                pq.heappush(queue, (d_next, p_next))
                
                if p_next in Ts:
                    t_base = p_next
                    for p_t in Ts:
                        if p_t != p_next:
                            visited[p_t] = p_last
                            pq.heappush(queue, (d_next, p_t))
                    
                if p_next == dst:
                    moves = [dst]
                    while moves[0] != src:
                        moves.insert(0, visited[moves[0]])
                        if moves[0] in Ts:
                            moves.insert(0, t_base)
                    printBoardWithMoves(board, moves)
                    return moves
    return []

def longest():
    pass

class KnightTests(unittest.TestCase):
    def setUp(self):
        print "In method", self._testMethodName

    def test_level1(self):
        # level 1
        self.assertTrue(validate(BOARD8, [(1, 2), (3, 3), (5, 4)]))
        self.assertFalse(validate(BOARD8, [(1, 2), (2, 3), (5, 4)]))
        self.assertFalse(validate("........ ........ ..B..... ........ ........ ........ ........ ........".split(), [(1, 2), (3, 3), (5, 4)]))
        self.assertFalse(validate("........ ........ ........ ..B..... ........ ........ ........ ........".split(), [(1, 2), (3, 3), (5, 4)]))
        self.assertTrue(validate("........ ........ ..R..... ........ ........ ........ ........ ........".split(), [(1, 2), (3, 3), (5, 4)]))
        self.assertTrue(validate("........ ...T.... ........ ...T.... ........ ........ ........ ........".split(), [(1, 2), (3, 1), (3, 3), (5, 4)]))
        self.assertFalse(validate("........ ........ ........ ...B.... ........ ........ ........ ........".split(), [(1, 2), (3, 3), (5, 4)]))
        
        # level 2~3
        self.assertTrue(3, len(compute(BOARD8, (1, 2), (5, 4))))
        self.assertTrue(3, len(shortest(BOARD8, (1, 2), (5, 4))))
        
        board = "........ ........ ........ ...R.... ........ ........ ........ ........".split()
        self.assertEqual(5, len(compute(board, (1, 2), (5, 4))))
        self.assertEqual(5, len(shortest(board, (1, 2), (5, 4))))
        
        board = "........ ...T.... ........ ...R.... ........ .......T ........ ........".split()
        self.assertEqual(4, len(compute(board, (1, 2), (5, 4))))
        self.assertEqual(4, len(shortest(board, (1, 2), (5, 4))))
        
        board = "..TB.... ...B.... ...B.... ...B.... ...B.... ...B.... ...B..T. ...B....".split()
        self.assertEqual(4, len(compute(board, (1, 2), (5, 4))))
        self.assertEqual(4, len(shortest(board, (1, 2), (5, 4))))
        
        # level 4
        board = BOARD32
        self.assertEqual(23, len(compute(board, (0, 0), (31, 31))))
        self.assertEqual(23, len(shortest(board, (0, 0), (31, 31))))
if __name__ == '__main__':
    unittest.main()        