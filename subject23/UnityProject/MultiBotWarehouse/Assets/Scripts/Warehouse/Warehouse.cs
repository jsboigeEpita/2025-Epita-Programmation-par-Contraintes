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
using static Solver;
using static Warehouse;
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
    private TMP_Text refillTextDebug;
    [SerializeField]
    private TMP_Text orderTextDebug;
    [SerializeField]
    private TMP_Text tasksTextDebug;
    [SerializeField]
    private TMP_Text mapTextDebug;
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
    private Dictionary<Robot.Role, Solver.Job[]> roleJobs;
    private Dictionary<Robot.Role, Task[]> flatRoleJobs;

    private IndexedPoint[] robotGoals = null;

    private void Awake()
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

        roleJobs = new Dictionary<Role, Job[]>();
        flatRoleJobs = new Dictionary<Role, Task[]>();
    }

    private void Start()
    {
        mapPath = Path.Combine(Application.persistentDataPath, "grid.ssv");
        Debug.Log("Outputting map to " + mapPath);

        using (StreamWriter writer = new StreamWriter(mapPath))
        {
            writer.WriteLine("height " + gridSize.x);
            writer.WriteLine("width " + gridSize.y);
            writer.WriteLine("map");

            for (int y = 0; y < gridSize.x; y++)
            {
                for (int x = 0; x < gridSize.y; x++)
                {
                    writer.Write(grid[y][x] ? "." : "@");
                }

                if (y != gridSize.x - 1)
                    writer.WriteLine("");
            }
        }

        wrapperMapPath = Path.Combine(Application.persistentDataPath, "map.ssv");
        Debug.Log("Outputting wrapperMap to " + wrapperMapPath);

        using (StreamWriter writer = new StreamWriter(wrapperMapPath))
        {
            writer.WriteLine("map_file=" + mapPath);
            writer.WriteLine("agents=" + robots.Length);
            writer.WriteLine("seed=0");
            writer.WriteLine("random_problem=0");
            writer.WriteLine("max_timestep=5000000");
            writer.WriteLine("max_comp_time=30000000");
        }
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
        tasksTextDebug.text = string.Join("\n", roleJobs[Role.Refill].Select(ele => ele.Debug()).ToArray());

        //roleJobs.Add(Role.Order, GenerateOrderJobs(orders));
        //flatRoleJobs.Add(Role.Order, roleJobs[Role.Order].Select(ele => ele.tasks).Aggregate(new List<Task>(), (acc, ele) => { acc.AddRange(ele); return acc; }).ToArray());
        //tasksTextDebug.text = string.Join("\n", roleJobs[Role.Order].Select(ele => ele.Debug()).ToArray());

        int[][] travelTimes = GenerateTravelTimes();

        assignments.Add(Robot.Role.Refill, Solver.Solve(assignedRobots[Robot.Role.Refill].Count, roleJobs[Role.Refill], travelTimes, verbose: false));
        //assignments.Add(Robot.Role.Order, Solver.Solve(assignedRobots[Robot.Role.Order].Count, roleJobs[Role.Order], travelTimes, verbose: false));

        refillTextDebug.text = AssignmentsToString(assignments[Robot.Role.Refill]);
        //orderTextDebug.text = AssignmentsToString(assignments[Robot.Role.Order]);

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
        bool isGoingToStart = true;

        while (robot.assignment.Count > 0)
        {
            Vector2Int currentPos = GetGridPosFromWorldPos(robot.controller.transform.position);

            Task currentTask = flatRoleJobs[robot.role][robot.assignment[0]];
            int goadId = isGoingToStart ? currentTask.startLocationId : currentTask.endLocationId;
            robot.goal = GetGridPosFromId(goadId);

            if (robot.lastPosition != currentPos)
            {
                computeGoals();

                

                robot.lastPosition = currentPos;

                /*
                mapTextDebug.text = "";
                for (int y = 0; y < gridSize.x; y++)
                {
                    for (int x = 0; x < gridSize.y; x++)
                    {
                        if (y == currentPos.x && x == currentPos.y)
                            mapTextDebug.text += "x";
                        else
                            mapTextDebug.text += grid[y][x] ? "." : "@";
                    }

                    if (y != gridSize.x - 1)
                        mapTextDebug.text += "\n";
                }
                */

                yield return null;
            }

            while (robotGoals == null)
            {
                computeGoals();
                yield return new WaitForSeconds(0.2f);
            }
                
            robot.controller.enabled = true;
            robot.controller.target = ConvertGrid2Pos(robotGoals[robot.id].point, robot.controller.transform.position.y);

            if (robot.goal == currentPos)
            {
                if (isGoingToStart == false)
                {
                    robot.assignment.RemoveAt(0);
                }

                isGoingToStart = !isGoingToStart;

                robot.lastPosition = new Vector2Int(int.MaxValue, int.MaxValue);
            }

            yield return new WaitForSeconds(0.2f);
        }

        robot.goal = robot.homePosition;

        while (robot.goal != robot.homePosition)
        {
            Vector2Int currentPos = GetGridPosFromWorldPos(robot.controller.transform.position);

            if (robot.lastPosition != currentPos)
            {
                computeGoals();
                robot.lastPosition = currentPos;
            }

            robot.controller.enabled = true;
            robot.controller.target = ConvertGrid2Pos(robotGoals[robot.id].point, robot.controller.transform.position.y);
        }
    }

    private void computeGoals()
    {
        /*
        if (!robots.Select(robot =>
                {
                    Vector2Int currentPos = GetGridPosFromWorldPos(robot.controller.transform.position);
                    return grid[currentPos.x][currentPos.y];
                }
            ).Aggregate(true, (acc, ele) => acc && ele)
        )
            return;
            
        AgentInfo[] agentInfos = new AgentInfo[robots.Length];

        for (int i = 0; i < robots.Length; i++)
        {
            agentInfos[i].agentId = robots[i].id;
            agentInfos[i].init = GetGridPosFromWorldPos(robots[i].controller.transform.position);
            agentInfos[i].goal = robots[i].goal;
        }

        List<IndexedPoint> temp = NextStep(agentInfos, robots.Length, wrapperMapPath).ToList();
        temp.Sort((ele1, ele2) => ele1.id.CompareTo(ele2.id));
        robotGoals = temp.ToArray();
        */

        robotGoals = new IndexedPoint[robots.Length];

        for (int i = 0; i < robots.Length; i++)
        {
            var pathfinderOptions = new AStar.Options.PathFinderOptions
            {
                PunishChangeDirection = true,
                UseDiagonals = false,
            };

            short[][] tiles = grid.Select(ele => ele.Select(subEle => subEle ? (short)1 : (short)0).ToArray()).ToArray();

            for (int k = 0; k < robots.Length; k++)
            {
                Vector2Int currentPos = GetGridPosFromWorldPos(robots[k].controller.transform.position);
                tiles[currentPos.x][currentPos.y] = 0;
            }

            WorldGrid worldGrid = new WorldGrid(ConvertMultidimensionalArrayToMultipleArrays(tiles));
            PathFinder pathfinder = new PathFinder(worldGrid, pathfinderOptions);

            Position[] path = pathfinder.FindPath(Vector2IntToPosition(GetGridPosFromWorldPos(robots[i].controller.transform.position)), Vector2IntToPosition(robots[i].goal));

            Debug.Log(path.Length);

            robotGoals[robots[i].id] = new IndexedPoint(i, PositionToVector2Int(path.Length >= 2 ? path[1] : path[0]));
        }
    }

    private Solver.Job[] GenerateRefillJobs()
    {
        List<Solver.Job> jobs = new List<Solver.Job>();

        foreach (ShelfManager shelf in shelves)
        {
            if (shelf.shelvingUnit.items.Where(ele => ele != null).Count() < shelf.shelvingUnit.items.Count)
            {
                jobs.Add(new Solver.Job(GetIdFromGridPos(GetGridPosFromWorldPos(sources.Find(ele => ele.furnitureIndex == shelf.furnitureIndex).gameObject.transform.position)), GetIdFromGridPos(GetGridPosFromWorldPos(shelf.shelvingUnit.deliveryPoint.position)), 0, Solver.Task.TaskType.Input));
            }
        }

        return jobs.ToArray();
    }

    private Solver.Job[] GenerateOrderJobs(string[][] orders)
    {
        List<Solver.Job> jobs = new List<Solver.Job>();

        short packerIndex = 0;

        foreach (string[] order in orders)
        {
            List<Solver.Task> tasks = new List<Solver.Task>();

            foreach (string demand in order)
            {
                int index = furnitures.names.FindIndex(ele => ele == demand);

                tasks.Add(new Solver.Task(GetIdFromGridPos(GetGridPosFromWorldPos(shelves.Find(ele => ele.furnitureIndex == index).gameObject.transform.position)), GetIdFromGridPos(GetGridPosFromWorldPos(packers[packerIndex].inputManager.transform.position)), 0, Solver.Task.TaskType.Shelf));
            }

            tasks.Add(new Solver.Task(GetIdFromGridPos(GetGridPosFromWorldPos(packers[packerIndex].outputManager.transform.position)), GetIdFromGridPos(GetGridPosFromWorldPos(outputs.First().transform.position)), 0, Solver.Task.TaskType.Packer));

            jobs.Add(new Solver.Job(tasks.ToArray()));

            packerIndex++;
            if (packerIndex == packers.Count)
            {
                Solver.Task lastTask = new Solver.Task(tasks[tasks.Count - 1].startLocationId, tasks[tasks.Count - 1].endLocationId, tasks[tasks.Count - 1].serviceTime, Solver.Task.TaskType.Pause);
                jobs.Add(new Solver.Job(lastTask));
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

    public string AssignmentsToString(int[][] array)
    {
        StringBuilder stringBuilder = new StringBuilder();

        for (int i = 0; i < array.Length; i++)
        {
            stringBuilder.Append(i);
            stringBuilder.Append(": ");
            for (int j = 0; j < array[i].Length; j++)
            {
                stringBuilder.Append(array[i][j]);
                stringBuilder.Append(",");
            }
            stringBuilder.Append("\n");
        }

        return stringBuilder.ToString();
    }

    private static T[,] ConvertMultidimensionalArrayToMultipleArrays<T>(T[][] array)
    {
        var result = new T[array.Length, array[0].Length];

        for (int i = 0; i < array.Length; i++)
            for (int j = 0; j < array[0].Length; j++)
            {
                result[i, j] = array[i][j];
            }

        return result;
    }

    private static Position Vector2IntToPosition(Vector2Int position)
    {
        return new Position(position.y, position.x);
    }

    private static Vector2Int PositionToVector2Int(Position position)
    {
        return new Vector2Int(position.Column, position.Row);
    }
}
