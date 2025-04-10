    using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEngine;

public class Warehouse : MonoBehaviour
{
    public static int gridScale = 10;

    public static Vector3Int convertPos2Grid(Vector3 position)
    {
        return new Vector3Int(Mathf.FloorToInt(position.x / gridScale), Mathf.FloorToInt(position.y / gridScale), Mathf.FloorToInt(position.z / gridScale));
    }

    public static Vector3 convertGrid2Pos(Vector3Int position)
    {
        return position * gridScale;
    }

    [Header("Settings")]
    [SerializeField]
    private bool enableGridDebug = true;

    [Header("Situation")]
    [SerializeField]
    private List<GameObject> sources;
    [SerializeField]
    private List<GameObject> robots;
    [SerializeField]
    private List<GameObject> shelves;
    [SerializeField]
    private List<GameObject> packers;
    [SerializeField]
    private List<GameObject> outputs;

    [Header("Grid")]
    [SerializeField]
    private Vector2Int gridSize;
    [SerializeField]
    private GameObject gridBlocksContainer;
    [SerializeField]
    private Transform gridOriginTransform;

    public string mapPath;
    public string wrapperMapPath;

    private List<GameObject>[] pointsOfInterest;
    
    public bool[][] grid;

    public void Awake()
    {
        pointsOfInterest = new List<GameObject>[]
        {
            sources,
            robots,
            shelves,
            packers,
            outputs,
        };

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
            grid[Mathf.FloorToInt((blockTransform.position.x - gridOriginTransform.position.x) / 10)][Mathf.FloorToInt((blockTransform.position.z - gridOriginTransform.position.z)) / 10] = false;
        }
    }

    public void Start()
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
                writer.WriteLine("agents=" + robots.Count);
                writer.WriteLine("seed=0");
                writer.WriteLine("random_problem=0");
                writer.WriteLine("max_timestep=5000000");
                writer.WriteLine("max_comp_time=30000000");
            }
        }
    }
}
