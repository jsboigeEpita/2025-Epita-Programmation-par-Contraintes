using System.Collections.Generic;
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

    [Header("Grid Space Settings")]
    [SerializeField]
    private Transform gridStart;
    [SerializeField]
    private Transform gridEnd;
    [SerializeField]
    private Vector2Int sourceVolume;
    [SerializeField]
    private Vector2Int sourceVolumeOffset;
    [SerializeField]
    private Vector2Int robotVolume;
    [SerializeField]
    private Vector2Int robotVolumeOffset;
    [SerializeField]
    private Vector2Int shelfVolume;
    [SerializeField]
    private Vector2Int shelfVolumeOffset;
    [SerializeField]
    private Vector2Int packerVolume;
    [SerializeField]
    private Vector2Int packerVolumeOffset;
    [SerializeField]
    private Vector2Int outputVolume;
    [SerializeField]
    private Vector2Int outputVolumeOffset;


    private Vector2Int[] volumes;
    private Vector2Int[] volumeOffsets;

    private List<GameObject>[] pointsOfInterest;

    private Vector2Int gridSize;
    private bool[][] grid;


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

        volumes = new Vector2Int[] {
            sourceVolume,
            robotVolume,
            shelfVolume,
            packerVolume,
            outputVolume,
        };

        volumeOffsets = new Vector2Int[] {
            sourceVolumeOffset,
            robotVolumeOffset,
            shelfVolumeOffset,
            packerVolumeOffset,
            outputVolumeOffset,
        };

        pointsOfInterest = new List<GameObject>[volumes.Length];

        gridSize = new Vector2Int(Mathf.FloorToInt(gridEnd.position.x - gridStart.position.x), Mathf.FloorToInt(gridEnd.position.y - gridStart.position.y));
        grid = new bool[gridSize.x][];
        for (int x = 0; x < gridSize.x; x++)
        {
            grid[x] = new bool[gridSize.y];
            for (int y = 0; y < gridSize.y; y++)
            {
                grid[x][y] = false;
                for (int i = 0; i < volumes.Length; i++)
                {
                    foreach (GameObject p in pointsOfInterest[i])
                    {
                        Vector3Int gridPos = convertPos2Grid(p.transform.position);
                        Vector2Int volume = volumes[i] - Vector2Int.one;

                        for (int vx = gridPos.x - volume.x + volumeOffsets[i].x; vx < gridPos.x + volume.x + volumeOffsets[i].x; vx++)
                        {
                            for (int vy = gridPos.z - volume.y + volumeOffsets[i].y; vy < gridPos.z + volume.y + volumeOffsets[i].y; vy++)
                            {
                                if (vx == x && vy == y)
                                {
                                    grid[x][y] = true;
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    public void Start()
    {
        if (enableGridDebug)
        {
            for (int x = 0; x < gridSize.x; x++)
            {
                for (int y = 0; y < gridSize.y; y++)
                { 
                    if (grid[x][y])
                    {
                        GameObject.CreatePrimitive(PrimitiveType.Cube).transform.localScale = Vector3.one * 2.5f;
                    }
                }
            }
        }
    }
}
