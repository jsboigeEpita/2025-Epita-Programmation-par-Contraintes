using Google.OrTools.ConstraintSolver;
using UnityEngine;

public class VRPSolver : MonoBehaviour
{
    struct Dependency
    {
        public int TaskA;
        public int TaskB;

        public Dependency(int taskA, int taskB)
        {
            TaskA = taskA;
            TaskB = taskB;
        }
    }

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {


        long[][] distanceMatrix = new long[][]{new long[]{ 0 , 1 },
                                             new long[]{ 1 , 0 }};

        long[] serviceTime = new long[] { 0, 0 };

        Dependency[] dependencies = new Dependency[] { new Dependency(0, 1) };

        // Assume you have these variables defined:
        int numNodes = /*<number of tasks>*/ 5 + /*<number of depots if needed>*/ 5;
        int numVehicles = 3;
        int depot = 0; // the starting (and possibly ending) depot index
        var manager = new RoutingIndexManager(numNodes, numVehicles, depot);
        var routing = new RoutingModel(manager);

        // Define a callback that returns the travel cost between nodes.
        long TransitCallback(long fromIndex, long toIndex)
        {
            int fromNode = manager.IndexToNode(fromIndex);
            int toNode = manager.IndexToNode(toIndex);
            return distanceMatrix[fromNode][toNode];
        }
        int transitCallbackIndex = routing.RegisterTransitCallback(TransitCallback);
        routing.SetArcCostEvaluatorOfAllVehicles(transitCallbackIndex);

        long serviceTimeCallback(long fromIndex, long toIndex)
        {
            int fromNode = manager.IndexToNode(fromIndex);
            // Here you might combine travel time and service duration.
            // For simplicity, assume travel time is given by distanceMatrix and you have a serviceTime[ ] array.
            return distanceMatrix[fromNode][manager.IndexToNode(toIndex)] + serviceTime[fromNode];
        }
        int serviceTimeCallbackIndex = routing.RegisterTransitCallback(serviceTimeCallback);

        routing.AddDimension(
            serviceTimeCallbackIndex,    // transit callback for time/ service cost
            30,                          // allow waiting time if needed, adjust as appropriate
            1000,                        // maximum time per route (tune the maximum value)
            false,                       // do not force start cumul to zero
            "Time");

        // Suppose dependency[i] holds the task index that must immediately follow task i (or -1 if none).
        foreach (Dependency dependency in dependencies)
        {
            int taskA = dependency.TaskA; // the predecessor
            int taskB = dependency.TaskB; // the dependent task

            // Convert to internal indices.
            long taskAIndex = manager.NodeToIndex(taskA);
            long taskBIndex = manager.NodeToIndex(taskB);

            // Enforce that the next task after A is B.
            // This effectively means no intervening tasks can be scheduled between A and B.
            routing.NextVar(taskAIndex).SetValue(taskBIndex);

            // Optionally, if using a time dimension, add: time[B] == time[A] + serviceTime[A] + travelTime(A, B).
            // This is implicitly enforced if the routing order is fixed.

            // Retrieve the cumulative time variables for tasks A and B.
            RoutingDimension timeDimension = routing.GetDimensionOrDie("Time");

            // Enforce that task B starts only after task A is finished.
            // Assuming serviceTime is the duration at task A and the travel time from task A to task B is in your distance matrix.
            long serviceTimeA = serviceTime[taskA];
            long travelTimeAB = distanceMatrix[taskA][taskB];

            long taskACompletion = timeDimension.CumulVar(manager.NodeToIndex(taskA)).Value() + serviceTimeA + travelTimeAB;
            long taskBStart = timeDimension.CumulVar(manager.NodeToIndex(taskB)).Value();

            // Here we try to ensure that task B starts no earlier than task A's completion time.
            // Note: This is conceptual because in the RoutingModel you typically embed these relationships
            // in the transit callback or during dimension creation.

            var searchParameters = operations_research_constraint_solver.DefaultRoutingSearchParameters();
            searchParameters.FirstSolutionStrategy = FirstSolutionStrategy.Types.Value.PathCheapestArc;
            Assignment solution = routing.SolveWithParameters(searchParameters);

            if (solution != null)
            {
                for (int vehicleId = 0; vehicleId < numVehicles; vehicleId++)
                {
                    Debug.Log($"Route for robot {vehicleId}:");
                    long index = routing.Start(vehicleId);
                    while (!routing.IsEnd(index))
                    {
                        Debug.Log($"{manager.IndexToNode(index)} -> ");
                        index = solution.Value(routing.NextVar(index));
                    }
                    Debug.Log("End");
                }
            }
            else
            {
                Debug.Log("No solution found");
            }
        }
    }
}


