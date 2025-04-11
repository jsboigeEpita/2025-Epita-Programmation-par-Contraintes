using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using TMPro;
using UnityEngine;
using static Warehouse.Robot;

public class Warehouse : MonoBehaviour
{
    public static int gridScale = 10;

    [System.Serializable]
    public struct Robot
    {
        public enum Role
        {
            Refill,
            Order
        }

        public Role role;
        public AutomatedRobotController controller;
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

    [Header("Settings")]
    [SerializeField]
    private bool enableGridDebug = true;

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
    }

    private void Start()
    {
        if (enableGridDebug)
        {
            mapPath = Path.Combine(Application.persistentDataPath, "grid.ssv");
            Debug.Log("Outputting map to " + mapPath);

            using (StreamWriter writer = new StreamWriter(mapPath))
            {
                writer.WriteLine("height " + gridSize.x);
                writer.WriteLine("width " + gridSize.y);
                writer.WriteLine("map");

                foreach (bool[] row in grid)
                {
                    writer.WriteLine(string.Join("", row.Select(ele => ele ? "." : "@").ToList()));
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

        string[][] orders = new string[0][];

        int[][] travelTimes = GenerateTravelTimes();

        Solver.Job[] refillJobs = GenerateRefillJobs();
        Solver.Job[] orderJobs = GenerateOrderJobs(orders);

        tasksTextDebug.text = string.Join("\n", refillJobs.Select(ele => ele.Debug()).ToArray());

        assignments.Add(Robot.Role.Refill, Solver.Solve(assignedRobots[Robot.Role.Refill].Count, refillJobs, travelTimes, verbose: false));
        assignments.Add(Robot.Role.Order, Solver.Solve(assignedRobots[Robot.Role.Order].Count, orderJobs, travelTimes, verbose: false));

        refillTextDebug.text = AssignmentsToString(assignments[Robot.Role.Refill]);
        orderTextDebug.text = AssignmentsToString(assignments[Robot.Role.Order]);
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
        return new Vector3Int(Mathf.FloorToInt((position.x - gridOriginTransform.position.x) / gridScale), Mathf.FloorToInt((position.y - gridOriginTransform.position.y) / gridScale), Mathf.FloorToInt((position.z - gridOriginTransform.position.z) / gridScale));
    }

    public Vector3 ConvertGrid2Pos(Vector3Int position)
    {
        return position * gridScale;
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
}
