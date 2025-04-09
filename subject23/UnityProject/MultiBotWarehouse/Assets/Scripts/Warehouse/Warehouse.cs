using System;
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
            string filePath = Path.Combine(Application.persistentDataPath, "grid.ssv");
            Debug.Log("Outputting grid to " + filePath);

            using (StreamWriter writer = new StreamWriter(filePath))
            {
                writer.WriteLine("height " + gridSize.y);
                writer.WriteLine("width " + gridSize.x);
                writer.WriteLine("map");

                foreach (bool[] row in grid)
                {
                    writer.WriteLine(string.Join("", row.Select(ele => ele ? "." : "@").ToList()));
                }
            }

        }
    }
}
