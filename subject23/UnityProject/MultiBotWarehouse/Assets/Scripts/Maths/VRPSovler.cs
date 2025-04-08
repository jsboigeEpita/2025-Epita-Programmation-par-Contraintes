using Google.OrTools.Sat;
using NUnit.Framework;
using System;
using System.Collections.Generic;
using System.Linq;
using Unity.VisualScripting;
using UnityEngine;

public class VRPSolver : MonoBehaviour
{
    struct Task
    {
        public int startLocationIndex;
        public int endLocationIndex;

        public Task( int startLocationIndex, int endLocationIndex)
        {
            this.startLocationIndex = startLocationIndex;
            this.endLocationIndex = endLocationIndex;
        }
    }

    public List<List<KeyValuePair<int, long>>> getPaths(List<int> tasksIds)
    {
        CpModel model = new CpModel();

        // Example data
        int numRobots = 2;
        int numLocations = 6;
        int horizon = 10000000; // maximum overall timeline length (here a large value to fulfill all tasks)
                                // Duration for each task (including service time, or service+travel if you wish)

        Task workbenchToDelivery = new Task(4, 5);
        Task AToWorkbench = new Task(0, 3);
        Task BToWorkbench = new Task(1, 3);
        Task CToWorkbench = new Task(2, 3);

        Task[] differentTasks = new Task[] { workbenchToDelivery, AToWorkbench, BToWorkbench, CToWorkbench };
        int numDifferentTasks = differentTasks.Length;

        int[][] locationsTravelTimes = new int[][] { 
        /*A*/   new int[] { 0,  2,  4, 21, 22, 31},
        /*B*/   new int[] { 2,  0,  2, 11, 12, 21},
        /*C*/   new int[] { 4,  2,  0,  3,  4, 13},
        /*W1*/  new int[] {21, 11,  3,  0,  1, 11},
        /*W2*/  new int[] {22, 12,  4,  1,  0, 10},
        /*L*/   new int[] {31, 21, 13, 11, 10,  0}
        };

        int[] taskIds = new int[] { 0, 1, 2, 2, 3, 3, 3 };
        int numTasksTotal = taskIds.Length;

        List<int> durations = new List<int>();
        foreach (int taskId in taskIds)
        {
            Task currentTask = differentTasks[taskId];
            durations.Add(locationsTravelTimes[currentTask.startLocationIndex][currentTask.endLocationIndex]);
        }
        //int[] durations = { 10, 21, 11, 11, 3, 3, 3 };


        // Values if tasks are assigned or not
        IntVar[][] isAssigned = new IntVar[numTasksTotal][];

        // Create arrays for start times, end times, and interval variables.
        IntVar[] startVars = new IntVar[numTasksTotal];
        IntVar[] endVars = new IntVar[numTasksTotal];
        IntervalVar[] taskIntervals = new IntervalVar[numTasksTotal];

        for (int i = 0; i < numTasksTotal; i++)
        {
            // Start times can range from 0 to horizon.
            startVars[i] = model.NewIntVar(0, horizon, $"start_{i}");
            // End time is determined by the start plus duration.
            endVars[i] = model.NewIntVar(0, horizon, $"end_{i}");
            // Create interval variable for the task.
            taskIntervals[i] = model.NewIntervalVar(startVars[i], durations[i], endVars[i], $"Task_{i}");
        }

        // TODO: add travel times even if the task aren't dependent
        // Assume travelTime is defined as a matrix with travelTime[i][j] for tasks i to j.
        int workbenchCraftTime = 32;

        // All of our subtasks must be fullfiled before that whe can deliver the final package
        for (int task = 1; task < numTasksTotal; task++)
        {
            model.Add(startVars[0] >= endVars[task] + workbenchCraftTime);
        }

        // for each task, one optional interval per robot.
        IntervalVar[][] robotTaskIntervals = new IntervalVar[numTasksTotal][];

        for (int i = 0; i < numTasksTotal; i++)
        {
            robotTaskIntervals[i] = new IntervalVar[numRobots];
            isAssigned[i] = new IntVar[numRobots];
            for (int r = 0; r < numRobots; r++)
            {
                // Create an optional interval variable for task i on robot r.
                // Create a Boolean variable that is true if task i is assigned to robot r.
                isAssigned[i][r] = model.NewBoolVar($"task_{i}_on_robot_{r}");
                robotTaskIntervals[i][r] = model.NewOptionalIntervalVar(startVars[i], durations[i],
                                                                        endVars[i],
                                                                        isAssigned[i][r], $"Task_{i}_R{r}");
            }
        }

        // For each robot, add the no-overlap constraint across the optional intervals.
        for (int r = 0; r < numRobots; r++)
        {
            List<IntervalVar> intervalsForRobot = new List<IntervalVar>();
            for (int i = 0; i < numTasksTotal; i++)
            {
                intervalsForRobot.Add(robotTaskIntervals[i][r]);
            }
            model.AddNoOverlap(intervalsForRobot);
        }

        for (int i = 0; i < numTasksTotal; i++)
        {
            IntVar[] assignments = new IntVar[numRobots];
            for (int r = 0; r < numRobots; r++)
            {
                // Assuming each optional interval has an associated Boolean variable.
                // Here we extract them or maintain a separate data structure.
                assignments[r] = isAssigned[i][r];
            }
            model.Add(LinearExpr.Sum(assignments) == 1);
        }

        IntVar makespan = model.NewIntVar(0, horizon, "makespan");
        model.AddMaxEquality(makespan, endVars);
        model.Minimize(makespan);

        for (int r = 0; r < numRobots; r++)
        {
            for (int i = 0; i < numTasksTotal; i++)
            {
                for (int j = 0; j < numTasksTotal; j++)
                {
                    if (i == j) continue;

                    // 1. Les deux tâches sont affectées au même robot
                    ILiteral[] bothAssigned = new ILiteral[] { isAssigned[i][r], isAssigned[j][r] };

                    // 2. Crée deux booléens : i avant j, ou j avant i
                    IntVar iBeforeJ = model.NewBoolVar($"i{i}_before_j{j}_robot{r}");
                    IntVar jBeforeI = model.NewBoolVar($"j{j}_before_i{i}_robot{r}");

                    // 3. Ils sont mutuellement exclusifs si les deux tâches sont affectées
                    model.Add(iBeforeJ + jBeforeI == 1).OnlyEnforceIf(bothAssigned);
                    model.Add(iBeforeJ + jBeforeI == 0).OnlyEnforceIf(isAssigned[i][r].Not());
                    model.Add(iBeforeJ + jBeforeI == 0).OnlyEnforceIf(isAssigned[j][r].Not());


                    // 4. Contraintes de transition
                    model.Add(startVars[j] >= endVars[i] + locationsTravelTimes[differentTasks[taskIds[i]].endLocationIndex][differentTasks[taskIds[j]].startLocationIndex])
                         .OnlyEnforceIf(iBeforeJ);

                    model.Add(startVars[i] >= endVars[j] + locationsTravelTimes[differentTasks[taskIds[j]].endLocationIndex][differentTasks[taskIds[i]].startLocationIndex])
                         .OnlyEnforceIf(jBeforeI);
                }
            }
        }

        // Create a solver instance.
        CpSolver solver = new CpSolver();

        // Optionally, you can set a time limit:
        // solver.StringParameters = "max_time_in_seconds:10";

        // Solve the model.
        CpSolverStatus status = solver.Solve(model);

        if (status == CpSolverStatus.Optimal || status == CpSolverStatus.Feasible)
        {
            List<List<KeyValuePair<int, long>>> results = new List<List<KeyValuePair<int, long>>> ();
            for (int r = 0; r < numRobots; r++)
            {
                results.Add(new List<KeyValuePair<int, long>> ());
                for (int i = 0; i < numTasksTotal; i++)
                {
                    if (solver.BooleanValue(isAssigned[i][r]))
                    {
                        results[r].Add(new KeyValuePair<int, long>(i, solver.Value(startVars[i])));
                    }
                }
            }
            return results;
        }
        else
        {
            Debug.Log("No solution found.");
            return null;
        }
    }
}
