using System;
using System.Diagnostics;
using System.Linq;
using System.Runtime.InteropServices;
using UnityEngine;

public class PathFindingCppWrapper
{
    public static class MapF
    {
        [StructLayout(LayoutKind.Sequential)]
        public struct cPoint
        {
            public int x;
            public int y;

            public cPoint(int x, int y)
            {
                this.x = x;
                this.y = y;
            }
        };

        [StructLayout(LayoutKind.Sequential)]
        public struct cIndexedPoint
        {
            public int id;
            public cPoint point;

            public cIndexedPoint(int id, cPoint point)
            {
                this.id = id;
                this.point = point;
            }
        };

        [StructLayout(LayoutKind.Sequential)]
        public struct cAgentInfo
        {
            public int agentId;
            public cPoint init;
            public cPoint goal;

            public cAgentInfo(int agentId, cPoint init, cPoint goal)
            {
                this.agentId = agentId;
                this.init = init;
                this.goal = goal;
            }
        };

        [DllImport("mapf", CallingConvention = CallingConvention.Cdecl)]
        public static extern void free_cIdPos(IntPtr arr);

        [DllImport("mapf", CallingConvention = CallingConvention.Cdecl)]
        public static extern IntPtr next_step_wrapper(
            [MarshalAs(UnmanagedType.LPArray, SizeParamIndex = 1)] cAgentInfo[] agent_info_arg,
            ulong count,
            [MarshalAs(UnmanagedType.LPStr)] string path
        );
    }

    [System.Serializable]
    public struct IndexedPoint
    {
        public int id;
        public Vector2Int point;

        public IndexedPoint(int id, Vector2Int point)
        {
            this.id = id;
            this.point = point;
        }
    };

    [System.Serializable]
    public struct AgentInfo
    {
        public int agentId;
        public Vector2Int init;
        public Vector2Int goal;

        public AgentInfo(int agentId, Vector2Int init, Vector2Int goal)
        {
            this.agentId = agentId;
            this.init = init;
            this.goal = goal;
        }
    };

    public static IndexedPoint[] NextStep(AgentInfo[] agentInfoArg, int count, string path)
    {
        IntPtr ptr = MapF.next_step_wrapper(agentInfoArg.Select(ele => new MapF.cAgentInfo(ele.agentId, new MapF.cPoint(ele.init.y, ele.init.x), new MapF.cPoint(ele.goal.y, ele.goal.x))).ToArray(), (ulong)count, path);

        MapF.cIndexedPoint[] managedArray = new MapF.cIndexedPoint[count];

        int structSize = Marshal.SizeOf(typeof(MapF.cIndexedPoint));
        for (int i = 0; i < count; i++)
        {
            IntPtr structPtr = new IntPtr(ptr.ToInt64() + i * structSize);
            managedArray[i] = Marshal.PtrToStructure<MapF.cIndexedPoint>(structPtr);
        }

        MapF.free_cIdPos(ptr);

        return managedArray.Select(ele => new IndexedPoint(ele.id, new Vector2Int(ele.point.y, ele.point.x))).ToArray();
    }
}
