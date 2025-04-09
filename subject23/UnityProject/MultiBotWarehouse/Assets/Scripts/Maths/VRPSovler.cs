using Google.OrTools.Sat;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

public class VRPSolver : MonoBehaviour
{
    [System.Serializable]
    public struct Job
    {

    }

    [System.Serializable]
    public struct Task
    {
        public enum TaskType
        {
            Other
        }

        public int startLocationId;
        public int endLocationId;
        public int precedence;
    }

    public List<List<int>> Do(int numRobots, int numLocations, (int, int, int)[] tasks, int[][] travelTimes, int[][] serviceTimes, long horizon = int.MaxValue)
    {
        CpModel model = new CpModel();

        int numTasks = tasks.Length;

        int[] travelDurations = new int[numTasks];
        for (int i = 0; i < numTasks; i++)
        {
            travelDurations[i] = travelTimes[tasks[i].Item1][tasks[i].Item2];
        }

        int[] serviceDurations = new int[numTasks];
        for (int i = 0; i < numTasks; i++)
        {
            serviceDurations[i] = serviceTimes[tasks[i].Item1][tasks[i].Item2];
        }

        IntVar[] startVars = new IntVar[numTasks];
        IntVar[] endVars = new IntVar[numTasks];
        IntervalVar[] taskIntervals = new IntervalVar[numTasks];

        for (int i = 0; i < numTasks; i++)
        {
            startVars[i] = model.NewIntVar(0, horizon, $"start_{i}");
            endVars[i] = model.NewIntVar(0, horizon, $"end_{i}");
            taskIntervals[i] = model.NewIntervalVar(startVars[i], travelDurations[i] + serviceDurations[i], endVars[i], $"interval_{i}");
        }
        /*
        for (int task = 1; task < numTasks; task++)
        {
            model.Add(startVars[startVars.Length - 1] >= endVars[task] + workbenchCraftTime);
        }

        // for each task, one optional interval per robot.
        IntervalVar[][] robotTaskIntervals = new IntervalVar[numTasksTotal][];

        // Values if tasks are assigned or not
        IntVar[][] isAssigned = new IntVar[numTasksTotal][];

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
            model.Add(LinearExpr.Sum(isAssigned[i]) == 1);
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
                    model.Add(startVars[j] >= endVars[i]
                        + locationsTravelTimes[differentTasks[tasksIds[i]].endLocationIndex][differentTasks[tasksIds[j]].startLocationIndex])
                         .OnlyEnforceIf(iBeforeJ);

                    model.Add(startVars[i] >= endVars[j]
                        + locationsTravelTimes[differentTasks[tasksIds[j]].endLocationIndex][differentTasks[tasksIds[i]].startLocationIndex])
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
            Debug.Log("Found a solution with status: " + status.ToString());

            List<List<int>> results = new List<List<int>>(numRobots);
            for (int r = 0; r < numRobots; r++)
            {
                var tempResult = new List<KeyValuePair<int, long>>(numTasksTotal);
                for (int i = 0; i < numTasksTotal; i++)
                {
                    if (solver.BooleanValue(isAssigned[i][r]))
                    {
                        tempResult.Add(new KeyValuePair<int, long>(i, solver.Value(startVars[i])));
                    }
                }
                tempResult.Sort((ele1, ele2) => ele1.Value.CompareTo(ele2.Value));
                results[r] = tempResult.Select(ele => ele.Key).ToList();
            }

            Debug.Log(results.ToString());
            return results;
        }
        else
        {
            Debug.Log("No solution found.");
            return null;
        }*/

        return null;
    }
}
