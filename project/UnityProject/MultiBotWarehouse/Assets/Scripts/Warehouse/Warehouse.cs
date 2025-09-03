using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using AStar;
using TMPro;
using UnityEngine;
using static PathFindingCppWrapper;
using static PlanningSolver;
using static Warehouse.Robot;

public class Warehouse : MonoBehaviour
{
    public static int gridScale = 10;

    [System.Serializable]
    public class Robot
    {
        public enum Role
        {
            Refill,
            Order
        }

        [NonSerialized]
        public int id;

        public Role role;
        public AutomatedRobotController controller;

        [NonSerialized]
        public Vector2Int lastPosition = new Vector2Int(int.MaxValue, int.MaxValue);
        [NonSerialized]
        public Vector2Int homePosition;

        [NonSerialized]
        public Vector2Int goal;
        [NonSerialized]
        public List<int> assignment;
    }

    [Header("Setup")]
    [SerializeField]
    private Furnitures furnitures;
    [SerializeField]
    private ClientOrderInteraction clientOrderInteraction;

    [Header("Situation")]
    [SerializeField]
    private List<SourceManager> sources;
    [SerializeField]
    private Robot[] robots;
    [SerializeField]
    private List<ShelfManager> shelves;
    [SerializeField]
    private List<PackerManager> packers;
    [SerializeField]
    private List<DeliveryManager> outputs;

    [Header("Grid")]
    [SerializeField]
    private Vector2Int gridSize;
    [SerializeField]
    private GameObject gridBlocksContainer;
    [SerializeField]
    private Transform gridOriginTransform;

    public string mapPath;
    public string wrapperMapPath;

    public bool[][] grid;

    private Dictionary<Robot.Role, int[][]> assignments;
    private Dictionary<Robot.Role, List<Robot>> assignedRobots;
    private Dictionary<Robot.Role, PlanningSolver.Job[]> roleJobs;
    private Dictionary<Robot.Role, Task[]> flatRoleJobs;
    private Vector2Int[] forbiddenGoals;

    private Vector2Int[] robotGoals = null;

    private void Start()
    {
        grid = new bool[gridSize.x][];
        for (int i = 0; i < gridSize.x; i++)
        {
            grid[i] = new bool[gridSize.y];
            for (int j = 0; j < gridSize.y; j++)
            {
                grid[i][j] = true;
            }
        }
        
        foreach (Transform blockTransform in gridBlocksContainer.GetComponentsInChildren<Transform>())
        {
            Vector2Int pos = GetGridPosFromWorldPos(blockTransform.position);
            grid[pos.x][pos.y] = false;
        }

        assignments = new Dictionary<Robot.Role, int[][]>();

        assignedRobots = new Dictionary<Role, List<Robot>>();
        foreach (Role role in Enum.GetValues(typeof(Role)))
        {
            assignedRobots.Add(role, new List<Robot>());
        }
        foreach (Robot robot in robots)
        {
            assignedRobots[robot.role].Add(robot);
        }

        List<Vector2Int> pointsOfInterests = new List<Vector2Int>();
        foreach (SourceManager source in sources)
        {
            pointsOfInterests.Add(GetGridPosFromWorldPos(source.transform.position));
        }
        foreach (ShelfManager shelf in shelves)
        {
            pointsOfInterests.Add(GetGridPosFromWorldPos(shelf.shelvingUnit.deliveryPoint.position));
        }
        foreach (PackerManager packer in packers)
        {
            pointsOfInterests.Add(GetGridPosFromWorldPos(packer.inputManager.transform.position));
            pointsOfInterests.Add(GetGridPosFromWorldPos(packer.outputManager.transform.position));
        }
        foreach (DeliveryManager delivery in outputs)
        {
            pointsOfInterests.Add(GetGridPosFromWorldPos(delivery.transform.position));
        }
        forbiddenGoals = pointsOfInterests.ToArray();

        roleJobs = new Dictionary<Role, Job[]>();
        flatRoleJobs = new Dictionary<Role, Task[]>();
    }

    public void OnClickProduceButton()
    {
        StartProduce();
    }

    private void StartProduce()
    {
        string[][] orders = clientOrderInteraction.orders.Select(ele => ele.order.ToArray()).ToArray();

        roleJobs.Add(Role.Refill, GenerateRefillJobs());
        flatRoleJobs.Add(Role.Refill, roleJobs[Role.Refill].Select(ele => ele.tasks).Aggregate(new List<Task>(), (acc, ele) => { acc.AddRange(ele); return acc; }).ToArray());

        //roleJobs.Add(Role.Order, GenerateOrderJobs(orders));
        //flatRoleJobs.Add(Role.Order, roleJobs[Role.Order].Select(ele => ele.tasks).Aggregate(new List<Task>(), (acc, ele) => { acc.AddRange(ele); return acc; }).ToArray());

        int[][] travelTimes = GenerateTravelTimes();

        assignments.Add(Robot.Role.Refill, PlanningSolver.Solve(assignedRobots[Robot.Role.Refill].Count, roleJobs[Role.Refill], travelTimes, verbose: false));
        //assignments.Add(Robot.Role.Order, Solver.Solve(assignedRobots[Robot.Role.Order].Count, roleJobs[Role.Order], travelTimes, verbose: false));

        int id = 0;

        for (int i = 0; i < assignedRobots[Role.Refill].Count; i++)
        {
            Robot refillRobot = assignedRobots[Robot.Role.Refill][i];

            refillRobot.assignment = assignments[Robot.Role.Refill][i].ToList();
            refillRobot.homePosition = GetGridPosFromWorldPos(refillRobot.controller.transform.position);
            refillRobot.id = id++;

            StartCoroutine(Runtime(refillRobot));
        }

        /*
        for (int i = 0; i < assignedRobots[Role.Refill].Count; i++)
        {
            Robot orderRobot = assignedRobots[Robot.Role.Order][i];

            orderRobot.assignment = assignments[Robot.Role.Order][i].ToList();
            orderRobot.homePosition = GetGridPosFromWorldPos(orderRobot.controller.transform.position);
            orderRobot.id = id++;

            StartCoroutine(RefillRuntime(orderRobot));
        }
        */
    }

    private IEnumerator Runtime(Robot robot)
    {
        while (robot.assignment.Count > 0)
        {
            Vector2Int currentPos = GetGridPosFromWorldPos(robot.controller.transform.position);

            Task currentTask = flatRoleJobs[robot.role][robot.assignment[0]];
            robot.controller.robotManager.taskType = currentTask.type;
            int goadId = robot.controller.robotManager.isTaking ? currentTask.startLocationId : currentTask.endLocationId;
            robot.goal = GetGridPosFromId(goadId);

            if (robot.lastPosition != currentPos)
            {
                computeGoals();
                robot.lastPosition = currentPos;
            }

            while (robotGoals == null)
            {
                computeGoals();
                yield return null;
            }
                
            robot.controller.enabled = true;
            robot.controller.target = ConvertGrid2Pos(robotGoals[robot.id], robot.controller.transform.position.y);

            if (Vector3.Distance(ConvertGrid2Pos(robot.goal, robot.controller.transform.position.y), robot.controller.transform.position) < 3f)
            {
                if (robot.controller.robotManager.isTaking == false)
                {
                    robot.assignment.RemoveAt(0);
                }

                robot.controller.robotManager.isTaking = !robot.controller.robotManager.isTaking;

                robot.lastPosition = new Vector2Int(int.MaxValue, int.MaxValue);
            }

            yield return null;
        }

        robot.goal = robot.homePosition;

        while (Vector3.Distance(ConvertGrid2Pos(robot.homePosition, robot.controller.transform.position.y), robot.controller.transform.position) > 3f)
        {
            Vector2Int currentPos = GetGridPosFromWorldPos(robot.controller.transform.position);

            if (robot.lastPosition != currentPos)
            {
                computeGoals();
                robot.lastPosition = currentPos;
            }

            robot.controller.enabled = true;
            robot.controller.target = ConvertGrid2Pos(robotGoals[robot.id], robot.controller.transform.position.y);

            yield return null;
        }

        robot.controller.enabled = false;
    }

    private void computeGoals()
    {
        robotGoals = PathSolver.ComputeNextMoves(grid, forbiddenGoals, robots.Select(robot => new PathSolver.Robot(robot.id, GetGridPosFromWorldPos(robot.controller.transform.position), robot.goal, robotGoals != null ? robotGoals[robot.id] : Vector2Int.one * int.MaxValue)).ToArray());
    }

    private PlanningSolver.Job[] GenerateRefillJobs()
    {
        List<PlanningSolver.Job> jobs = new List<PlanningSolver.Job>();

        foreach (ShelfManager shelf in shelves)
        {
            if (shelf.shelvingUnit.items.Where(ele => ele != null).Count() < shelf.shelvingUnit.items.Count)
            {
                jobs.Add(new PlanningSolver.Job(GetIdFromGridPos(GetGridPosFromWorldPos(sources.Find(ele => ele.furnitureIndex == shelf.furnitureIndex).gameObject.transform.position)), GetIdFromGridPos(GetGridPosFromWorldPos(shelf.shelvingUnit.deliveryPoint.position)), 0, PlanningSolver.Task.TaskType.Input));
            }
        }

        return jobs.ToArray();
    }

    private PlanningSolver.Job[] GenerateOrderJobs(string[][] orders)
    {
        List<PlanningSolver.Job> jobs = new List<PlanningSolver.Job>();

        short packerIndex = 0;

        foreach (string[] order in orders)
        {
            List<PlanningSolver.Task> tasks = new List<PlanningSolver.Task>();

            foreach (string demand in order)
            {
                int index = furnitures.names.FindIndex(ele => ele == demand);

                tasks.Add(new PlanningSolver.Task(GetIdFromGridPos(GetGridPosFromWorldPos(shelves.Find(ele => ele.furnitureIndex == index).gameObject.transform.position)), GetIdFromGridPos(GetGridPosFromWorldPos(packers[packerIndex].inputManager.transform.position)), 0, PlanningSolver.Task.TaskType.Shelf));
            }

            tasks.Add(new PlanningSolver.Task(GetIdFromGridPos(GetGridPosFromWorldPos(packers[packerIndex].outputManager.transform.position)), GetIdFromGridPos(GetGridPosFromWorldPos(outputs.First().transform.position)), 0, PlanningSolver.Task.TaskType.Packer));

            jobs.Add(new PlanningSolver.Job(tasks.ToArray()));

            packerIndex++;
            if (packerIndex == packers.Count)
            {
                PlanningSolver.Task lastTask = new PlanningSolver.Task(tasks[tasks.Count - 1].startLocationId, tasks[tasks.Count - 1].endLocationId, tasks[tasks.Count - 1].serviceTime, PlanningSolver.Task.TaskType.Pause);
                jobs.Add(new PlanningSolver.Job(lastTask));
                packerIndex = 0;
            }
        }

        return jobs.ToArray();
    }

    private int[][] GenerateTravelTimes()
    {
        int[][] travelTimes = new int[gridSize.x * gridSize.y][];
        for (int i = 0; i < gridSize.x * gridSize.y; i++)
        {
            travelTimes[i] = new int[gridSize.x * gridSize.y];
        }

        List<Vector2Int> allPos = new List<Vector2Int>();

        for (int i = 0; i < gridSize.x; i++)
        {
            for (int j = 0; j < gridSize.y; j++)
            {
                allPos.Add(new Vector2Int(i, j));
            }
        }

        for (int i = 0; i < allPos.Count; i++)
        {
            for (int j = 0; j < allPos.Count; j++)
            {
                travelTimes[GetIdFromGridPos(allPos[i])][GetIdFromGridPos(allPos[j])] = Math.Abs(allPos[i].x - allPos[i].y) + Math.Abs(allPos[i].y - allPos[i].y);
            }
        }

        return travelTimes;
    }

    public Vector3Int ConvertPos2Grid(Vector3 position)
    {
        return new Vector3Int(Mathf.RoundToInt((position.x - gridOriginTransform.position.x) / gridScale), Mathf.RoundToInt((position.y - gridOriginTransform.position.y) / gridScale), Mathf.RoundToInt((position.z - gridOriginTransform.position.z) / gridScale));
    }

    public Vector3 ConvertGrid2Pos(Vector2Int position, float height)
    {
        return new Vector3(position.x * gridScale, height, position.y * gridScale) + gridOriginTransform.position;
    }

    public Vector2Int GetGridPosFromWorldPos(Vector3 worldPos)
    {
        Vector3Int gridPos = ConvertPos2Grid(worldPos);

        return new Vector2Int(gridPos.x, gridPos.z);
    }

    public int GetIdFromGridPos(Vector2Int gridPos)
    {
        return gridPos.x * gridSize.y + gridPos.y;
    }

    public Vector2Int GetGridPosFromId(int id)
    {
        int rem;
        int div = Math.DivRem(id, gridSize.y, out rem);
        return new Vector2Int(div, rem);
    }
}
