using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.UIElements;

public class WarehouseShelf : MonoBehaviour
{
    private struct TemporaryMesh
    {
        public List<Vector3> vertices;
        public List<int> triangles;

        public TemporaryMesh(List<Vector3> vertices, List<int> triangles)
        {
            this.vertices = vertices;
            this.triangles = triangles;
        }
    }

    [Header("Settings")]
    [SerializeField]
    private int stackAmount;
    [SerializeField]
    private float spacing;
    [SerializeField]
    private float heightSpacing;
    [SerializeField]
    private float pillarSize;
    [SerializeField]
    private float platformThickness;
    [SerializeField]
    private float platformAttachementThickness;
    [SerializeField]
    private float spaceFromGround;

    [Header("References")]
    [SerializeField]
    private GameObject itemGameObject;
    [SerializeField]
    private Material structureMaterial;
    [SerializeField]
    private Material shelfMaterial;

    [Header("Buttons")]
    [SerializeField]
    private bool generateMeshButton = false;
    [SerializeField]
    private bool rotateButton = false;

    private MeshFilter meshFilter;
    private MeshRenderer meshRenderer;
    private MeshCollider meshCollider;

    private Collider itemCollider;

    public List<GameObject> shelves;
    public GameObject pusher;
    public List<Vector3> platformMaxXPositions;
    public List<Vector3> platformMinXPositions;

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

        GenerateMesh();
    }

    private void Update()
    {
        if (generateMeshButton)
        {
            generateMeshButton = false;
            GenerateMesh();
        }

        if (rotateButton)
        {
            rotateButton = false;
            DoOneRotation();
        }
    }

    private void DoOneRotation()
    {
        StartCoroutine(LerpShelves(2f));
    }

    private IEnumerator LerpShelves(float duration)
    {
        float elapsed = 0f;

        while (elapsed < duration)
        {
            elapsed += Time.deltaTime;

            float t = Mathf.Clamp01(elapsed / duration);

            for (int i = 0; i < shelves.Count; i++)
            {
                shelves[i].transform.localPosition = Vector3.Lerp(platformMaxXPositions[i], platformMaxXPositions[(i + 1) % platformMaxXPositions.Count], t);
            }

            yield return null;
        }

        for (int i = 0; i < shelves.Count; i++)
        {
            shelves[i].transform.localPosition = platformMaxXPositions[(i + 1) % platformMaxXPositions.Count];
        }
    }

    private void GenerateMesh()
    {
        #region Generate Mesh
        Vector3 itemBounds = itemCollider.bounds.size;

        Mesh mesh = new Mesh();

        List<Vector3> vertices = new List<Vector3>();
        List<int> triangles = new List<int>();

        #region Pillars
        float maxX = (itemBounds.x / 2) + spacing + (pillarSize / 2);
        float minX = (-itemBounds.x / 2) - spacing - (pillarSize / 2);
        float maxZ = (itemBounds.z / 2) + spacing + (pillarSize / 2);
        float minZ = (-itemBounds.z / 2) - spacing - (pillarSize / 2);

        Vector3[] pillarPositions = new Vector3[4]
        {
            new Vector3(minX, 0, minZ),
            new Vector3(minX, 0, maxZ),
            new Vector3(maxX, 0, minZ),
            new Vector3(maxX, 0, maxZ)
        };

        float height = (itemBounds.y + heightSpacing) * (stackAmount + 3);

        foreach (Vector3 pillarPosition in pillarPositions)
        {
            TemporaryMesh pillar = LinkPointsByCube(pillarPosition, pillarPosition + new Vector3(0, height, 0), Vector3.right, pillarSize * 2, pillarSize * 2, vertices.Count);
            vertices.AddRange(pillar.vertices);
            triangles.AddRange(pillar.triangles);
        }

        foreach (Vector2Int indices in new Vector2Int[] { new Vector2Int(0, 1), new Vector2Int(2, 3), new Vector2Int(3, 0), new Vector2Int(0, 2), new Vector2Int(1, 3) })
        {
            TemporaryMesh pillar = LinkPointsByCube(pillarPositions[indices.x] + new Vector3(0, height, 0), pillarPositions[indices.y] + new Vector3(0, height, 0), Vector3.up, pillarSize, pillarSize, vertices.Count);
            vertices.AddRange(pillar.vertices);
            triangles.AddRange(pillar.triangles);
        }
        #endregion

        float levelHeight = heightSpacing + itemBounds.y;

        platformMaxXPositions = new List<Vector3>();
        platformMaxXPositions.Add(new Vector3(maxX - pillarSize / 2, spaceFromGround, 0));
        for (int i = 0; i < stackAmount; i++)
        {
            platformMaxXPositions.Add(new Vector3(maxX - pillarSize / 2, spaceFromGround + levelHeight * (i + 1), maxZ));
        }
        platformMaxXPositions.Add(new Vector3(maxX - pillarSize / 2, spaceFromGround + levelHeight * (stackAmount + 1), 0));
        for (int i = stackAmount - 1; i >= 0; i--)
        {
            platformMaxXPositions.Add(new Vector3(maxX - pillarSize / 2, spaceFromGround + levelHeight * (i + 1), minZ));
        }
        platformMaxXPositions.Add(new Vector3(maxX - pillarSize / 2, spaceFromGround, 0));

        platformMinXPositions = new List<Vector3>();
        platformMinXPositions.Add(new Vector3(minX + pillarSize / 2, spaceFromGround, 0));
        for (int i = 0; i < stackAmount; i++)
        {
            platformMinXPositions.Add(new Vector3(minX + pillarSize / 2, spaceFromGround + levelHeight * (i + 1), maxZ));
        }
        platformMinXPositions.Add(new Vector3(minX + pillarSize / 2, spaceFromGround + levelHeight * (stackAmount + 1), 0));
        for (int i = stackAmount - 1; i >= 0; i--)
        {
            platformMinXPositions.Add(new Vector3(minX + pillarSize / 2, spaceFromGround + levelHeight * (i + 1), minZ));
        }
        platformMinXPositions.Add(new Vector3(minX + pillarSize / 2, spaceFromGround, 0));

        #region Platforms Attachements
        foreach (List<Vector3> platformPositions in new List<Vector3>[2] { platformMaxXPositions, platformMinXPositions })
        {
            Vector3 direction = platformPositions[0].x > platformMinXPositions[0].x ? Vector3.right : -Vector3.right;

            for (int i = 0; i < platformPositions.Count - 1; i++)
            {
                TemporaryMesh pillar = LinkPointsByCube(platformPositions[i], platformPositions[i + 1], direction, pillarSize, pillarSize, vertices.Count);
                vertices.AddRange(pillar.vertices);
                triangles.AddRange(pillar.triangles);
            }

            foreach (Vector3[] points in new Vector3[][]
            {
                new Vector3[2]
                {
                    platformPositions[stackAmount] + new Vector3(0, levelHeight, 0),
                    platformPositions[platformPositions.Count - 1 - stackAmount] + new Vector3(0, levelHeight, 0)
                },
                new Vector3[2]
                {
                    platformPositions[stackAmount],
                    platformPositions[platformPositions.Count - 1 - stackAmount]
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
                    platformPositions[stackAmount],
                    platformPositions[platformPositions.Count - 2]
                },
                new Vector3[2]
                {
                    platformPositions[1],
                    platformPositions[platformPositions.Count - 1 - stackAmount]
                },
                new Vector3[2]
                {
                    platformPositions[0].x > platformMinXPositions[0].x ? platformPositions[stackAmount] + new Vector3(0, levelHeight, 0) : pillarPositions[1] + new Vector3(0, height, 0),
                    platformPositions[0].x > platformMinXPositions[0].x ? pillarPositions[2] + new Vector3(0, height, 0) : platformPositions[platformPositions.Count - 1 - stackAmount] + new Vector3(0, levelHeight, 0)
                }
            })
            {
                TemporaryMesh topSlider1 = LinkPointsByCube(points[0], points[1], direction, pillarSize, pillarSize, vertices.Count);
                vertices.AddRange(topSlider1.vertices);
                triangles.AddRange(topSlider1.triangles);
            }
        }
        #endregion

        #region Pickup
        
        #endregion

        #region Platform
        for (int i = 0; i < platformMaxXPositions.Count - 1; i++)
        {
            Vector3 pos = new Vector3((platformMaxXPositions[i].x - platformMinXPositions[i].x) / 2, platformMaxXPositions[i].y, platformMaxXPositions[i].z);
            TemporaryMesh platform = LinkPointsByCube(platformMaxXPositions[i] - pos, platformMinXPositions[i] - pos, -Vector3.forward, platformThickness, (maxZ - minZ) / 4);
            AddChildGameObject("Shelf " + i, pos, platform, shelves);
        }
        #endregion

        mesh.vertices = vertices.ToArray();
        mesh.triangles = triangles.ToArray();

        mesh.RecalculateNormals();

        meshFilter.mesh = mesh;

        meshRenderer.sharedMaterial = structureMaterial;
        meshCollider.sharedMesh = mesh;
        #endregion
    }

    private TemporaryMesh LinkPointsByCube(Vector3 A, Vector3 B, Vector3 up, float rightThickness, float depthThickness, int offset = 0)
    {
        List<Vector3> vertices = new List<Vector3>();
        List<int> triangles = new List<int>();

        Vector3 direction = (B - A).normalized;
        Vector3 right = Vector3.Cross(direction, up).normalized;

        Vector3 v0 = A + (-rightThickness * right - depthThickness * up);
        Vector3 v1 = A + (-rightThickness * right + depthThickness * up);
        Vector3 v2 = A + (rightThickness * right - depthThickness * up);
        Vector3 v3 = A + (rightThickness * right + depthThickness * up);

        Vector3 v4 = B + (-rightThickness * right - depthThickness * up);
        Vector3 v5 = B + (-rightThickness * right + depthThickness * up);
        Vector3 v6 = B + (rightThickness * right - depthThickness * up);
        Vector3 v7 = B + (rightThickness * right + depthThickness * up);

        vertices.Add(v0);
        vertices.Add(v1);
        vertices.Add(v2);
        vertices.Add(v3);
        vertices.Add(v4);
        vertices.Add(v5);
        vertices.Add(v6);
        vertices.Add(v7);

        triangles.Add(offset + 0);
        triangles.Add(offset + 1);
        triangles.Add(offset + 3);
        triangles.Add(offset + 0);
        triangles.Add(offset + 3);
        triangles.Add(offset + 2);

        triangles.Add(offset + 4);
        triangles.Add(offset + 7);
        triangles.Add(offset + 5);
        triangles.Add(offset + 4);
        triangles.Add(offset + 6);
        triangles.Add(offset + 7);

        triangles.Add(offset + 0);
        triangles.Add(offset + 5);
        triangles.Add(offset + 1);
        triangles.Add(offset + 0);
        triangles.Add(offset + 4);
        triangles.Add(offset + 5);

        triangles.Add(offset + 2);
        triangles.Add(offset + 3);
        triangles.Add(offset + 7);
        triangles.Add(offset + 2);
        triangles.Add(offset + 7);
        triangles.Add(offset + 6);

        triangles.Add(offset + 0);
        triangles.Add(offset + 2);
        triangles.Add(offset + 6);
        triangles.Add(offset + 0);
        triangles.Add(offset + 6);
        triangles.Add(offset + 4);

        triangles.Add(offset + 1);
        triangles.Add(offset + 7);
        triangles.Add(offset + 3);
        triangles.Add(offset + 1);
        triangles.Add(offset + 5);
        triangles.Add(offset + 7);

        triangles.Reverse();

        return new TemporaryMesh(vertices, triangles);
    }

    private void AddChildGameObject(string name, Vector3 position, TemporaryMesh temporaryMesh, List<GameObject> childList)
    {
        GameObject child = new GameObject(name);
        child.transform.SetParent(transform);
        child.transform.localPosition = position;
        child.transform.localRotation = Quaternion.identity;
        child.transform.localScale = Vector3.one;
        MeshFilter meshFilter = child.AddComponent<MeshFilter>();
        MeshRenderer meshRenderer = child.AddComponent<MeshRenderer>();
        MeshCollider meshCollider = child.AddComponent<MeshCollider>();

        Mesh customMesh = new Mesh();
        customMesh.vertices = temporaryMesh.vertices.ToArray();
        customMesh.triangles = temporaryMesh.triangles.ToArray();
        customMesh.RecalculateNormals();
        meshFilter.mesh = customMesh;
        meshRenderer.material = shelfMaterial;

        meshCollider.sharedMesh = customMesh;

        childList.Add(child);
    }
}
