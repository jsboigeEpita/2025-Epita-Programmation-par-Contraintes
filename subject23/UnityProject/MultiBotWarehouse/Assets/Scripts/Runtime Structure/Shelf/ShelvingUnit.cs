using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using static RuntimeStructure;

public class ShelvingUnit : MonoBehaviour
{
    [Header("Settings")]
    [SerializeField]
    private int levelCount = 4;
    [SerializeField]
    private float spacing = 1;
    [SerializeField]
    private float heightSpacing = 3;
    [SerializeField]
    private float pillarSize = 0.2f;
    [SerializeField]
    private float platformThickness = 0.1f;
    [SerializeField]
    private float spaceFromGround = 1;
    [SerializeField]
    private float speed = 2f;

    [Header("References")]
    [SerializeField]
    private GameObject itemGameObject;
    [SerializeField]
    private Material structureMaterial;
    [SerializeField]
    private Material shelfMaterial;

    [Header("Buttons")]
    [SerializeField]
    private bool rotateButton = false;

    private MeshFilter meshFilter;
    private MeshRenderer meshRenderer;
    private MeshCollider meshCollider;

    private Collider itemCollider;

    private List<GameObject> shelves;

    private List<Vector3> platformMaxXPositions;
    private List<Vector3> platformMinXPositions;

    private bool isRolling = false;
    private int currentShelfOffset = 0;

    private void Start()
    {
        #region Get Components
        meshFilter = this.GetComponent<MeshFilter>();
        if (meshFilter == null)
            Debug.LogError(this.name + ": meshFilter is null.");

        meshRenderer = this.GetComponent<MeshRenderer>();
        if (meshRenderer == null)
            Debug.LogError(this.name + ": meshRenderer is null.");

        meshCollider = this.GetComponent<MeshCollider>();
        if (meshCollider == null)
            Debug.LogError(this.name + ": meshCollider is null.");

        itemCollider = itemGameObject.GetComponent<Collider>();
        if (itemCollider == null)
            Debug.LogError(this.name + "/" + itemCollider.name + ": itemCollider is null.");
        #endregion

        shelves = new List<GameObject>();
        GenerateMesh();
    }

    private void Update()
    {
        if (rotateButton)
        {
            rotateButton = false;
            DoOneRotation();
        }
    }

    private void DoOneRotation()
    {
        if (!isRolling)
        {
            StartCoroutine(LerpShelves(speed));
        }
    }

    private IEnumerator LerpShelves(float duration)
    {
        isRolling = true;

        float elapsed = 0f;

        for (int i = 0; i < shelves.Count; i++)
        {
            shelves[i].GetComponent<Shelf>().Activate();
        }

        while (elapsed < duration)
        {
            elapsed += Time.deltaTime;

            float t = Mathf.Clamp01(elapsed / duration);

            for (int i = 0; i < shelves.Count; i++)
            {
                shelves[i].transform.localPosition = Vector3.Lerp(platformMaxXPositions[(currentShelfOffset + i) % shelves.Count], platformMaxXPositions[(currentShelfOffset + i + 1) % shelves.Count], t);
            }

            yield return null;
        }

        for (int i = 0; i < shelves.Count; i++)
        {
            shelves[i].transform.localPosition = platformMaxXPositions[(currentShelfOffset + i + 1) % shelves.Count];

            shelves[i].GetComponent<Shelf>().Deactivate();
        }

        currentShelfOffset = (currentShelfOffset + 1) % shelves.Count;
        isRolling = false;
    }

    private void AddChildSheld(string name, Vector3 position, Shape shape)
    {
        GameObject child = new GameObject(name);

        child.transform.SetParent(transform);
        child.transform.localPosition = position;
        child.transform.localRotation = Quaternion.identity;
        child.transform.localScale = Vector3.one;

        MeshFilter meshFilter = child.AddComponent<MeshFilter>();
        Mesh customMesh = new Mesh();
        customMesh.vertices = shape.vertices.ToArray();
        customMesh.triangles = shape.triangles.ToArray();
        customMesh.RecalculateNormals();
        meshFilter.mesh = customMesh;

        MeshRenderer meshRenderer = child.AddComponent<MeshRenderer>();
        meshRenderer.material = shelfMaterial;

        BoxCollider boxCollider = child.AddComponent<BoxCollider>();
        boxCollider.center = shape.vertices.Aggregate(Vector3.zero, (acc, x) => acc + x) / shape.vertices.Count;
        List<float> shapeX = shape.vertices.Select(v => v.x).ToList();
        List<float> shapeY = shape.vertices.Select(v => v.y).ToList();
        List<float> shapeZ = shape.vertices.Select(v => v.z).ToList();
        boxCollider.size = new Vector3(shapeX.Max() - shapeX.Min(), shapeY.Max() - shapeY.Min(), shapeZ.Max() - shapeZ.Min());

        float triggerHeight = itemCollider.bounds.size.y + heightSpacing;
        BoxCollider boxTrigger = child.AddComponent<BoxCollider>();
        boxTrigger.enabled = false;
        boxTrigger.isTrigger = true;
        boxTrigger.center = boxCollider.center + Vector3.up * (boxCollider.size.y / 2 + triggerHeight / 2 - spacing / 2);
        boxTrigger.size = new Vector3(boxCollider.size.x, boxCollider.size.y + triggerHeight - spacing, boxCollider.size.z);

        /*
        Rigidbody rigidbody = child.AddComponent<Rigidbody>();
        rigidbody.isKinematic = true;
        rigidbody.useGravity = false;
        */

        Shelf shelf = child.AddComponent<Shelf>();
        shelf.Initialize(boxCollider, boxTrigger, name => name.Contains(itemGameObject.name));

        shelves.Add(child);
    }

    private void GenerateMesh()
    {
        Vector3 itemBounds = itemCollider.bounds.size;

        Mesh mesh = new Mesh();

        List<Vector3> vertices = new List<Vector3>();
        List<int> triangles = new List<int>();

        #region Pillars
        float maxX = (itemBounds.x / 2) + spacing + pillarSize * 0.25f;
        float minX = (-itemBounds.x / 2) - spacing - pillarSize * 0.25f;
        float maxZ = itemBounds.z + spacing + pillarSize * 0.25f;
        float minZ = -itemBounds.z - spacing - pillarSize * 0.25f;

        Vector3[] pillarPositions = new Vector3[4]
        {
            new Vector3(minX, 0, minZ),
            new Vector3(minX, 0, maxZ),
            new Vector3(maxX, 0, minZ),
            new Vector3(maxX, 0, maxZ)
        };

        float height = (itemBounds.y + heightSpacing) * (levelCount + 3);

        foreach (Vector3 pillarPosition in pillarPositions)
        {
            Shape pillar = LinkPointsByCube(pillarPosition, pillarPosition + new Vector3(0, height, 0), Vector3.right, pillarSize, pillarSize, vertices.Count);
            vertices.AddRange(pillar.vertices);
            triangles.AddRange(pillar.triangles);
        }

        foreach (Vector2Int indices in new Vector2Int[] { new Vector2Int(0, 1), new Vector2Int(2, 3), new Vector2Int(3, 0), new Vector2Int(0, 2), new Vector2Int(1, 3) })
        {
            Shape pillar = LinkPointsByCube(pillarPositions[indices.x] + new Vector3(0, height, 0), pillarPositions[indices.y] + new Vector3(0, height, 0), Vector3.up, pillarSize, pillarSize, vertices.Count);
            vertices.AddRange(pillar.vertices);
            triangles.AddRange(pillar.triangles);
        }
        #endregion

        float levelHeight = heightSpacing + itemBounds.y;

        platformMaxXPositions = new List<Vector3>();
        platformMaxXPositions.Add(new Vector3((itemBounds.x / 2) + spacing, spaceFromGround, 0));
        for (int i = 0; i < levelCount; i++)
        {
            platformMaxXPositions.Add(new Vector3((itemBounds.x / 2) + spacing, spaceFromGround + levelHeight * (i + 1), maxZ));
        }
        platformMaxXPositions.Add(new Vector3((itemBounds.x / 2) + spacing, spaceFromGround + levelHeight * (levelCount + 1), 0));
        for (int i = levelCount - 1; i >= 0; i--)
        {
            platformMaxXPositions.Add(new Vector3((itemBounds.x / 2) + spacing, spaceFromGround + levelHeight * (i + 1), minZ));
        }
        platformMaxXPositions.Add(new Vector3((itemBounds.x / 2) + spacing, spaceFromGround, 0));

        platformMinXPositions = new List<Vector3>();
        platformMinXPositions.Add(new Vector3((-itemBounds.x / 2) - spacing, spaceFromGround, 0));
        for (int i = 0; i < levelCount; i++)
        {
            platformMinXPositions.Add(new Vector3((-itemBounds.x / 2) - spacing, spaceFromGround + levelHeight * (i + 1), maxZ));
        }
        platformMinXPositions.Add(new Vector3((-itemBounds.x / 2) - spacing, spaceFromGround + levelHeight * (levelCount + 1), 0));
        for (int i = levelCount - 1; i >= 0; i--)
        {
            platformMinXPositions.Add(new Vector3((-itemBounds.x / 2) - spacing, spaceFromGround + levelHeight * (i + 1), minZ));
        }
        platformMinXPositions.Add(new Vector3((-itemBounds.x / 2) - spacing, spaceFromGround, 0));

        #region Platforms Attachements
        foreach (List<Vector3> platformPositions in new List<Vector3>[2] { platformMaxXPositions, platformMinXPositions })
        {
            Vector3 direction = platformPositions[0].x > platformMinXPositions[0].x ? Vector3.right : -Vector3.right;

            for (int i = 0; i < platformPositions.Count - 1; i++)
            {
                Shape pillar = LinkPointsByCube(platformPositions[i], platformPositions[i + 1], direction, pillarSize * 0.75f, pillarSize * 0.75f, vertices.Count);
                vertices.AddRange(pillar.vertices);
                triangles.AddRange(pillar.triangles);
            }

            foreach (Vector3[] points in new Vector3[][]
            {
                new Vector3[2]
                {
                    platformPositions[levelCount] + new Vector3(0, levelHeight, 0),
                    platformPositions[platformPositions.Count - 1 - levelCount] + new Vector3(0, levelHeight, 0)
                },
                new Vector3[2]
                {
                    platformPositions[levelCount],
                    platformPositions[platformPositions.Count - 1 - levelCount]
                },
                new Vector3[2]
                {
                    platformPositions[1],
                    platformPositions[platformPositions.Count - 2]
                },
                new Vector3[2]
                {
                    platformPositions[1] - new Vector3(0, levelHeight, 0),
                    platformPositions[platformPositions.Count - 2] - new Vector3(0, levelHeight, 0)
                },
                new Vector3[2]
                {
                    platformPositions[levelCount],
                    platformPositions[platformPositions.Count - 2]
                },
                new Vector3[2]
                {
                    platformPositions[1],
                    platformPositions[platformPositions.Count - 1 - levelCount]
                },
                new Vector3[2]
                {
                    platformPositions[0].x > platformMinXPositions[0].x ? platformPositions[levelCount] + new Vector3(0, levelHeight, 0) : pillarPositions[1] + new Vector3(0, height, 0),
                    platformPositions[0].x > platformMinXPositions[0].x ? pillarPositions[2] + new Vector3(0, height, 0) : platformPositions[platformPositions.Count - 1 - levelCount] + new Vector3(0, levelHeight, 0)
                }
            })
            {
                Shape topSlider1 = LinkPointsByCube(points[0], points[1], direction, pillarSize * 0.75f, pillarSize * 0.75f, vertices.Count);
                vertices.AddRange(topSlider1.vertices);
                triangles.AddRange(topSlider1.triangles);
            }
        }
        #endregion

        #region Platform
        for (int i = 0; i < platformMaxXPositions.Count - 1; i++)
        {
            Vector3 pos = new Vector3((platformMaxXPositions[i].x - platformMinXPositions[i].x) / 2, platformMaxXPositions[i].y, platformMaxXPositions[i].z);
            Shape platform = LinkPointsByCube(platformMaxXPositions[i] - pos - Vector3.right * pillarSize * 0.75f, platformMinXPositions[i] - pos + Vector3.right * pillarSize * 0.75f, -Vector3.forward, platformThickness, (maxZ - minZ) / 4);
            AddChildSheld("Shelf " + i, pos, platform);
        }
        #endregion

        mesh.vertices = vertices.ToArray();
        mesh.triangles = triangles.ToArray();

        mesh.RecalculateNormals();

        meshFilter.mesh = mesh;

        meshRenderer.sharedMaterial = structureMaterial;
        meshCollider.sharedMesh = mesh;
    }
}
