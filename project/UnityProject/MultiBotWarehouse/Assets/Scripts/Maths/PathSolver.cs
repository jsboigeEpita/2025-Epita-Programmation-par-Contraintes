using Google.OrTools.Sat;
using System.Collections.Generic;
using System;
using UnityEngine;
using System.Linq;

public class PathSolver
{
    public struct Robot
    {
        public int id;
        public Vector2Int pos;
        public Vector2Int goal;
        public Vector2Int lastMove;

        public Robot(int id, Vector2Int pos, Vector2Int goal, Vector2Int lastMove)
        {
            this.id = id;
            this.pos = pos;
            this.goal = goal;
            this.lastMove = lastMove;
        }
    }

    public static Vector2Int[] ComputeNextMoves(bool[][] grid, Vector2Int[] forbiddenGoals, Robot[] robots)
    {
        int gridWidth = grid.Length;
        int gridHeight = grid[0].Length;

        CpModel model = new CpModel();
        int robotCount = robots.Length;

        List<Vector2Int> candidateMoves = new List<Vector2Int>
        {
            new Vector2Int(0, 0),   // Stay
            new Vector2Int(0, 1),   // Up
            new Vector2Int(0, -1),  // Down
            new Vector2Int(1, 0),   // Right
            new Vector2Int(-1, 0)   // Left
        };

        List<List<Vector2Int>> candidateMovesPerRobot = new List<List<Vector2Int>>();
        for (int i = 0; i < robots.Length; i++)
        {
            Robot robot = robots[i];

            List<Vector2Int> validMoves = new List<Vector2Int>();

            foreach (Vector2Int move in candidateMoves)
            {
                int newX = robot.pos.x + move.x;
                int newY = robot.pos.y + move.y;

                Vector2Int newPos = new Vector2Int(newX, newY);
                if (newX >= 0
                    && newX < gridWidth
                    && newY >= 0
                    && newY < gridHeight
                    && grid[newX][newY]
                    && (newPos == robots[i].goal || !forbiddenGoals.Contains(newPos))
                    && !robots.Where(robot => robot.id != robots[i].id).Select(robot => robot.pos).Contains(newPos))
                    validMoves.Add(newPos);
            }

            candidateMovesPerRobot.Add(validMoves);
        }

        List<IntVar> moveVars = new List<IntVar>();
        for (int i = 0; i < robotCount; i++)
        {
            int n = candidateMovesPerRobot[i].Count;
            moveVars.Add(model.NewIntVar(0, n - 1, $"move_robot_{i}"));
        }

        List<IntVar> newXVars = new List<IntVar>();
        List<IntVar> newYVars = new List<IntVar>();

        for (int i = 0; i < robotCount; i++)
        {
            List<Vector2Int> movesForRobot = candidateMovesPerRobot[i];

            int n = movesForRobot.Count;

            int[] candidateX = new int[n];
            int[] candidateY = new int[n];

            for (int j = 0; j < n; j++)
            {
                candidateX[j] = movesForRobot[j].x;
                candidateY[j] = movesForRobot[j].y;
            }

            IntVar newX = model.NewIntVar(0, gridWidth - 1, $"newX_robot_{i}");
            IntVar newY = model.NewIntVar(0, gridHeight - 1, $"newY_robot_{i}");

            model.AddElement(moveVars[i], candidateX, newX);
            model.AddElement(moveVars[i], candidateY, newY);
            newXVars.Add(newX);
            newYVars.Add(newY);
        }

        for (int i = 0; i < robotCount; i++)
        {
            for (int j = i + 1; j < robotCount; j++)
            {
                IntVar eqX = model.NewBoolVar($"eqX_robot_{i}_robot_{j}");
                IntVar eqY = model.NewBoolVar($"eqY_robot_{i}_robot_{j}");

                model.Add(newXVars[i] == newXVars[j]).OnlyEnforceIf(eqX);
                model.Add(newXVars[i] != newXVars[j]).OnlyEnforceIf(eqX.Not());
                model.Add(newYVars[i] == newYVars[j]).OnlyEnforceIf(eqY);
                model.Add(newYVars[i] != newYVars[j]).OnlyEnforceIf(eqY.Not());

                model.Add(eqX + eqY <= 1);
            }
        }

        List<IntVar> costVars = new List<IntVar>();
        for (int i = 0; i < robotCount; i++)
        {
            Robot robot = robots[i];
            List<Vector2Int> movesForRobot = candidateMovesPerRobot[i];
            int n = movesForRobot.Count;
            int[] candidateCosts = new int[n];
            for (int j = 0; j < n; j++)
            {
                int pathLength = ComputeShortestPath(grid, movesForRobot[j], robot.goal) * 2;
                int candidateCost = (pathLength >= 0) ? pathLength : gridWidth * gridHeight;

                if (movesForRobot[j] == robot.pos && movesForRobot[j] != robot.goal && n > 1)
                {
                    candidateCost += 3;
                }

                if (robot.lastMove != Vector2Int.one * int.MaxValue)
                {
                    Vector2Int expectedPos = robot.pos + robot.lastMove;
                    if (movesForRobot[j] != expectedPos)
                    {
                        candidateCost += 1;
                    }
                }

                candidateCosts[j] = candidateCost;
            }

            IntVar costVar = model.NewIntVar(0, gridWidth * gridHeight, $"cost_robot_{i}");
            model.AddElement(moveVars[i], candidateCosts, costVar);
            costVars.Add(costVar);
        }
        model.Minimize(LinearExpr.Sum(costVars));

        CpSolver solver = new CpSolver();
        // solver.StringParameters = "max_time_in_seconds:0.5";
        CpSolverStatus status = solver.Solve(model);
        Vector2Int[] result = new Vector2Int[robotCount];

        if (status == CpSolverStatus.Optimal || status == CpSolverStatus.Feasible)
        {
            for (int i = 0; i < robotCount; i++)
            {
                result[robots[i].id] = new Vector2Int((int)solver.Value(newXVars[i]), (int)solver.Value(newYVars[i]));
            }
        }

        return result;
    }

    private static int ComputeShortestPath(bool[][] grid, Vector2Int start, Vector2Int goal)
    {
        int gridWidth = grid.Length;
        int gridHeight = grid[0].Length;

        if (start == goal)
            return 0;

        Queue<Vector2Int> queue = new Queue<Vector2Int>();
        bool[,] visited = new bool[gridWidth, gridHeight];

        queue.Enqueue(start);
        visited[start.x, start.y] = true;
        int steps = 0;

        Vector2Int[] directions = new Vector2Int[]
        {
        new Vector2Int(0, 1),    // Up
        new Vector2Int(0, -1),   // Down
        new Vector2Int(1, 0),    // Right
        new Vector2Int(-1, 0)    // Left
        };

        while (queue.Count > 0)
        {
            int currentLevelCount = queue.Count;
            steps++;

            for (int i = 0; i < currentLevelCount; i++)
            {
                Vector2Int current = queue.Dequeue();

                foreach (Vector2Int dir in directions)
                {
                    Vector2Int neighbor = new Vector2Int(current.x + dir.x, current.y + dir.y);

                    if (neighbor.x < 0 || neighbor.x >= gridWidth ||
                        neighbor.y < 0 || neighbor.y >= gridHeight)
                    {
                        continue;
                    }

                    if (!grid[neighbor.x][neighbor.y])
                        continue;

                    if (visited[neighbor.x, neighbor.y])
                        continue;

                    if (neighbor == goal)
                        return steps;

                    visited[neighbor.x, neighbor.y] = true;
                    queue.Enqueue(neighbor);
                }
            }
        }

        return -1;
    }

}
