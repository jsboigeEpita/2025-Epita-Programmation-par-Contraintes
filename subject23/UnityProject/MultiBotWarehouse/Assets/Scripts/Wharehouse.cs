using System.Collections.Generic;
using UnityEngine;

public class Wharehouse : MonoBehaviour
{
    public static int gridScale = 5;

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
    private bool enableInstantiation = true;
    [SerializeField]
    private bool enableGridDebug = true;

    [Header("Spawners")]
    [SerializeField]
    private Transform sourceSpawner;
    [SerializeField]
    private Transform robotSpawner;
    [SerializeField]
    private Transform shelfSpawner;
    [SerializeField]
    private Transform packerSpawner;
    [SerializeField]
    private Transform outputSpawner;

    [Header("Prefabs")]
    [SerializeField]
    private GameObject sourceGameObject;
    [SerializeField]
    private GameObject robotGameObject;
    [SerializeField]
    private GameObject shelfGameObject;
    [SerializeField]
    private GameObject packerGameObject;
    [SerializeField]
    private GameObject outputGameObject;

    [Header("Placement Settings")]
    [SerializeField]
    private float spacing;
    [SerializeField]
    private Vector2Int sourceDispatch;
    [SerializeField]
    private Vector2Int robotDispatch;
    [SerializeField]
    private Vector2Int shelfDispatch;
    [SerializeField]
    private Vector2Int packerDispatch;
    [SerializeField]
    private Vector2Int outputDispatch;

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


    private Transform[] spawners;
    private GameObject[] prefabs;
    private Vector2Int[] dispatches;
    private Vector2Int[] volumes;
    private Vector2Int[] volumeOffsets;

    public List<GameObject>[] pointsOfInterest;

    private Vector2Int gridSize;
    private bool[][] grid;


    public void Awake()
    {
        spawners = new Transform[]
        {
            sourceSpawner,
            robotSpawner,
            shelfSpawner,
            packerSpawner,
            outputSpawner,
        };

        prefabs = new GameObject[] {
            sourceGameObject,
            robotGameObject,
            shelfGameObject,
            packerGameObject,
            outputGameObject,
        };

        dispatches = new Vector2Int[] { 
            sourceDispatch,
            robotDispatch,
            shelfDispatch,
            packerDispatch,
            outputDispatch,
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
                    Vector3Int gridPos = convertPos2Grid(spawners[i].position);
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

    public void Start()
    {
        if (enableInstantiation)
        {
            for (int i = 0; i < prefabs.Length; i++)
            {
                for (int x = 0; x < dispatches[i].x; x++)
                {
                    for (int y = 0; y < dispatches[i].y; y++)
                    {
                        GameObject instanciated = GameObject.Instantiate(prefabs[i], spawners[i]);
                        instanciated.transform.localPosition = new Vector3(x, 0, y) * spacing;
                        pointsOfInterest[i].Add(instanciated);
                    }
                }
            }
        }

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
