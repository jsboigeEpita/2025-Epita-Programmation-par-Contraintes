using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using static RuntimeStructure;

public class LoaderUnit : MonoBehaviour
{
    [Header("Settings")]
    [SerializeField]
    private float spacing = 1;
    [SerializeField]
    private float pillarSize = 0.2f;
    [SerializeField]
    private float platformThickness = 0.1f;
    [SerializeField]
    private float width = 2f;
    [SerializeField]
    private float height = 2f;
    [SerializeField]
    private float depth = 2f;
    [SerializeField]
    private float speed = 2f;

    [Header("References")]
    [SerializeField]
    private GameObject itemGameObject;
    [SerializeField]
    private Material structureMaterial;
    [SerializeField]
    private Material loaderMaterial;

    [Header("Buttons")]
    [SerializeField]
    private bool loadButton = false;
    [SerializeField]
    private bool switchButton = false;

    private MeshFilter meshFilter;
    private MeshRenderer meshRenderer;
    private MeshCollider meshCollider;

    private Collider itemCollider;

    private GameObject loader;

    private Vector3 loadPos;
    private Vector3 unloadPos;

    private bool isLoading = false;

    public bool isReadyToLoad { get; private set; } = false;

    public void Fill(float spacing, float pillarSize, float platformThickness, float width, float height, float depth, float speed, GameObject itemGameObject, Material structureMaterial, Material loaderMaterial)
    {
        this.spacing = spacing;
        this.pillarSize = pillarSize;
        this.platformThickness = platformThickness;
        this.width = width;
        this.height = height;
        this.depth = depth;
        this.speed = speed;
        this.itemGameObject = itemGameObject;
        this.structureMaterial = structureMaterial;
        this.loaderMaterial = loaderMaterial;
    }

    public void Initialize()
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

    private void Start()
    {
        Initialize();
    }

    private void Update()
    {
        if (loadButton)
        {
            loadButton = false;
            Load();
        }

        if (switchButton)
        {
            switchButton = false;
            Switch();
        }
    }

    private void Load()
    {
        if (!isLoading)
        {
            StartCoroutine(LerpLoad(speed));
        }
    }
    private void Switch()
    {
        if (!isLoading)
        {
            StartCoroutine(LerpSwitch(speed));
        }
    }

    private IEnumerator LerpLoad(float duration)
    {
        isLoading = true;

        float elapsed = 0f;

        while (elapsed < duration)
        {
            elapsed += Time.deltaTime;

            float t = Mathf.Clamp01(elapsed / duration);

            loader.transform.localPosition = Vector3.Lerp((isReadyToLoad ? unloadPos : loadPos), (!isReadyToLoad ? unloadPos : loadPos), t);

            yield return null;
        }

        loader.transform.localPosition = !isReadyToLoad ? unloadPos : loadPos;

        isLoading = false;
        isReadyToLoad = !isReadyToLoad;
    }

    private IEnumerator LerpSwitch(float duration)
    {
        isLoading = true;

        float elapsed = 0f;

        Vector3 eulerAngles = loader.transform.localEulerAngles;

        while (elapsed < duration / 3)
        {
            elapsed += Time.deltaTime;

            float t = Mathf.Clamp01(elapsed / duration * 3);

            loader.transform.localEulerAngles = Vector3.Lerp(eulerAngles, eulerAngles + Vector3.right * 90 * (isReadyToLoad ? -1 : 1), t);

            yield return null;
        }

        loader.transform.localEulerAngles = eulerAngles + Vector3.right * 90 * (isReadyToLoad ? -1 : 1);

        elapsed = 0f;

        while (elapsed < duration / 3)
        {
            elapsed += Time.deltaTime;

            float t = Mathf.Clamp01(elapsed / duration * 3);

            loader.transform.localPosition = Vector3.Lerp((isReadyToLoad ? unloadPos : loadPos), (!isReadyToLoad ? unloadPos : loadPos), t);

            yield return null;
        }

        loader.transform.localPosition = !isReadyToLoad ? unloadPos : loadPos;

        elapsed = 0f;

        while (elapsed < duration / 3)
        {
            elapsed += Time.deltaTime;

            float t = Mathf.Clamp01(elapsed / duration * 3);

            loader.transform.localEulerAngles = Vector3.Lerp(eulerAngles + Vector3.right * 90 * (isReadyToLoad ? -1 : 1), eulerAngles + Vector3.right * 180 * (isReadyToLoad ? -1 : 1), t);

            yield return null;
        }

        loader.transform.localEulerAngles = eulerAngles;

        isLoading = false;
        isReadyToLoad = !isReadyToLoad;
    }

    private void GenerateMesh()
    {
        Vector3 itemBounds = itemCollider.bounds.size;

        Mesh mesh = new Mesh();

        List<Vector3> vertices = new List<Vector3>();
        List<int> triangles = new List<int>();

        #region Structure
        Vector3[] pillarPositions = new Vector3[]
        {
            new Vector3((itemBounds.x / 2) + spacing, 0, 0),
            new Vector3((-itemBounds.x / 2) - spacing, 0, 0),
        };

        foreach (Vector3 pillarPosition in pillarPositions)
        {
            Shape pillar = LinkPointsByCube(pillarPosition, pillarPosition + new Vector3(0, height, 0), Vector3.right, pillarSize, pillarSize, vertices.Count);
            vertices.AddRange(pillar.vertices);
            triangles.AddRange(pillar.triangles);
        }

        Vector3[] supportPositions = new Vector3[]
        {
            new Vector3((itemBounds.x / 2) + spacing, height, -width / 2),
            new Vector3((-itemBounds.x / 2) - spacing, height, -width / 2)
        };

        foreach (Vector3 supportPosition in supportPositions)
        {
            Shape support = LinkPointsByCube(supportPosition, supportPosition + new Vector3(0, 0, width), Vector3.up, pillarSize, pillarSize, vertices.Count);
            vertices.AddRange(support.vertices);
            triangles.AddRange(support.triangles);
        }
        #endregion

        #region Platform
        Vector3 middle = (supportPositions[0] + supportPositions[1]) / 2;
        Shape platform = LinkPointsByCube(supportPositions[0] + Vector3.forward * width / 2 - Vector3.up * middle.y, supportPositions[1] + Vector3.forward * width / 2 - Vector3.up * middle.y, Vector3.up, platformThickness, depth);
        AddChildLoader("Platform", middle, platform);
        #endregion

        #region Positions
        loadPos = middle;
        unloadPos = middle + Vector3.forward * width;
        #endregion

        mesh.vertices = vertices.ToArray();
        mesh.triangles = triangles.ToArray();
        mesh.RecalculateNormals();
        meshFilter.mesh = mesh;

        meshRenderer.sharedMaterial = structureMaterial;
        meshCollider.sharedMesh = mesh;
    }

    private void AddChildLoader(string name, Vector3 position, Shape shape)
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
        meshRenderer.material = loaderMaterial;

        BoxCollider boxCollider = child.AddComponent<BoxCollider>();
        boxCollider.center = shape.vertices.Aggregate(Vector3.zero, (acc, x) => acc + x) / shape.vertices.Count;
        List<float> shapeX = shape.vertices.Select(v => v.x).ToList();
        List<float> shapeY = shape.vertices.Select(v => v.y).ToList();
        List<float> shapeZ = shape.vertices.Select(v => v.z).ToList();
        boxCollider.size = new Vector3(shapeX.Max() - shapeX.Min(), shapeY.Max() - shapeY.Min(), shapeZ.Max() - shapeZ.Min());

        Rigidbody rigidbody = child.AddComponent<Rigidbody>();
        rigidbody.isKinematic = true;
        rigidbody.useGravity = false;

        loader = child;
    }
}
