using System;
using System.Diagnostics;
using System.Linq;
using System.Runtime.InteropServices;

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
        public static extern int test(int i);

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
    public struct Point
    {
        public int x;
        public int y;

        public Point(int x, int y)
        {
            this.x = x;
            this.y = y;
        }
    };

    [System.Serializable]
    public struct IndexedPoint
    {
        public int id;
        public Point point;

        public IndexedPoint(int id, Point point)
        {
            this.id = id;
            this.point = point;
        }
    };

    [System.Serializable]
    public struct AgentInfo
    {
        public int agentId;
        public Point init;
        public Point goal;

        public AgentInfo(int agentId, Point init, Point goal)
        {
            this.agentId = agentId;
            this.init = init;
            this.goal = goal;
        }
    };

    public static IndexedPoint[] NextStep(AgentInfo[] agentInfoArg, int count, string path)
    {
        IntPtr ptr = MapF.next_step_wrapper(agentInfoArg.Select(ele => new MapF.cAgentInfo(ele.agentId, new MapF.cPoint(ele.init.x, ele.init.y), new MapF.cPoint(ele.goal.x, ele.goal.y))).ToArray(), (ulong)count, path);

        MapF.cIndexedPoint[] managedArray = new MapF.cIndexedPoint[count];

        int structSize = Marshal.SizeOf(typeof(MapF.cIndexedPoint));
        for (int i = 0; i < count; i++)
        {
            IntPtr structPtr = new IntPtr(ptr.ToInt64() + i * structSize);
            managedArray[i] = Marshal.PtrToStructure<MapF.cIndexedPoint>(structPtr);
        }

        MapF.free_cIdPos(ptr);

        return managedArray.Select(ele => new IndexedPoint(ele.id, new Point(ele.point.x, ele.point.y))).ToArray();
    }
}
