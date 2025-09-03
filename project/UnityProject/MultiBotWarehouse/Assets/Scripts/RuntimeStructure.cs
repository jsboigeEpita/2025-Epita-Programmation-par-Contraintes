using System.Collections.Generic;
using UnityEngine;

public static class RuntimeStructure
{
    public struct Shape
    {
        public List<Vector3> vertices;
        public List<int> triangles;

        public Shape(List<Vector3> vertices, List<int> triangles)
        {
            this.vertices = vertices;
            this.triangles = triangles;
        }
    }

    public static Shape LinkPointsByCube(Vector3 A, Vector3 B, Vector3 up, float rightThickness, float depthThickness, int offset = 0)
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

        return new Shape(vertices, triangles);
    }
}
