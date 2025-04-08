using Google.OrTools.Sat;
using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

public class VRPSolver : MonoBehaviour
{
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        CpModel model = new CpModel();

        // Example data
        int numTasks = 7;
        int numRobots = 2;
        int horizon = 10000000; // maximum overall timeline length (here a large value to fulfill all tasks)
                            // Duration for each task (including service time, or service+travel if you wish)
        int[] durations = { 10, 21, 11, 11, 3, 3, 3 };

        int[][] travelTimes = new int[][] { 
        /* Workbench => Delivery */     new int[] { 10, 31, 21, 21, 13, 13, 13},
        /* A => Workbench */            new int[] { 00, 21, 11, 11, 03, 03, 03},
        /* B => Workbench */            new int[] { 00, 21, 11, 11, 03, 03, 03},
        /* B => Workbench */            new int[] { 00, 21, 11, 11, 03, 03, 03},
        /* C => Workbench */            new int[] { 00, 21, 11, 11, 03, 03, 03},
        /* C => Workbench */            new int[] { 00, 21, 11, 11, 03, 03, 03},
        /* C => Workbench */            new int[] { 00, 21, 11, 11, 03, 03, 03} };


        // Values if tasks are assigned or not
        IntVar[][] isAssigned = new IntVar[numTasks][];

        // Create arrays for start times, end times, and interval variables.
        IntVar[] startVars = new IntVar[numTasks];
        IntVar[] endVars = new IntVar[numTasks];
        IntervalVar[] taskIntervals = new IntervalVar[numTasks];

        for (int i = 0; i < numTasks; i++)
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
        for (int task = 1; task < numTasks; task++)
        {
            model.Add(startVars[0] >= endVars[task] + workbenchCraftTime);
        }

        // for each task, one optional interval per robot.
        IntervalVar[][] robotTaskIntervals = new IntervalVar[numTasks][];

        for (int i = 0; i < numTasks; i++)
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
            for (int i = 0; i < numTasks; i++)
            {
                intervalsForRobot.Add(robotTaskIntervals[i][r]);
            }
            model.AddNoOverlap(intervalsForRobot);
        }

        for (int i = 0; i < numTasks; i++)
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
            for (int i = 0; i < numTasks; i++)
            {
                for (int j = 0; j < numTasks; j++)
                {
                    if (i == j) continue;

                    // 1. Les deux tâches sont affectées au même robot
                    ILiteral[] bothAssigned = new ILiteral[] { isAssigned[i][r], isAssigned[j][r] };

                    // 2. Crée deux booléens : i avant j, ou j avant i
                    IntVar iBeforeJ = model.NewBoolVar($"i{i}_before_j{j}_robot{r}");
                    IntVar jBeforeI = model.NewBoolVar($"j{j}_before_i{i}_robot{r}");

                    // 3. Ils sont mutuellement exclusifs si les deux tâches sont affectées
                    model.Add(iBeforeJ + jBeforeI == 1).OnlyEnforceIf(bothAssigned);

                    // 4. Contraintes de transition
                    model.Add(startVars[j] >= endVars[i] + travelTimes[i][j])
                         .OnlyEnforceIf(new ILiteral[] { isAssigned[i][r], isAssigned[j][r], iBeforeJ });

                    model.Add(startVars[i] >= endVars[j] + travelTimes[j][i])
                         .OnlyEnforceIf(new ILiteral[] { isAssigned[i][r], isAssigned[j][r], jBeforeI });

                    // 5. Si les deux tâches ne sont pas affectées au robot r, iBeforeJ et jBeforeI == 0
                    model.Add(iBeforeJ == 0).OnlyEnforceIf(isAssigned[i][r].Not());
                    model.Add(iBeforeJ == 0).OnlyEnforceIf(isAssigned[j][r].Not());
                    model.Add(jBeforeI == 0).OnlyEnforceIf(isAssigned[i][r].Not());
                    model.Add(jBeforeI == 0).OnlyEnforceIf(isAssigned[j][r].Not());
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
            Debug.Log("Optimal solution found:");
            for (int i = 0; i < numTasks; i++)
            {
                for (int r = 0; r < numRobots; r++)
                {
                    if (solver.BooleanValue(isAssigned[i][r]))
                    {
                        Debug.Log($"Task {i}: durations: {solver.Value(startVars[i])} => {solver.Value(endVars[i])}, by: {r}");
                    }
                }  
            }
        }
        else
        {
            Debug.Log("No solution found.");
        }
    }
}
