from ortools.sat.python import cp_model

def multi_robot_scheduling_example():
    model = cp_model.CpModel()

    # --- Problem data ---
    num_robots = 3
    num_tasks = 3
    
    # Locations (indices 0..3, with 0 as the 'base' if desired)
    # For simplicity, let's say tasks 1, 2, 3 occur at locations 1, 2, 3
    # distances[locA][locB] = travel time from locA to locB
    distances = [
        [0,  2,  3,  4],  # from location 0 to others
        [2,  0,  2,  3],  # from location 1 to others
        [3,  2,  0,  2],  # from location 2 to others
        [4,  3,  2,  0],  # from location 3 to others
    ]
    
    # For each task, define its location and a duration needed to do the task
    task_locations = [1, 2, 3]  # location for tasks 0, 1, 2
    task_durations = [3, 2, 2]  # how long each task takes
    
    # We discretize time in some simple range
    # In reality, you'd figure out a tighter upper bound or use intervals
    # For example, let's say the maximum time horizon is 20
    max_time = 20
    
    # --- Decision variables ---
    # 1) A "start time" variable for each task & robot
    #    We'll only use it if the task is assigned to that robot
    start_time = {}
    for r in range(num_robots):
        for t in range(num_tasks):
            start_time[(r, t)] = model.NewIntVar(0, max_time, f"start_r{r}_t{t}")

    # 2) An "assigned" boolean variable: x[r,t] = 1 if robot r does task t
    assigned = {}
    for r in range(num_robots):
        for t in range(num_tasks):
            assigned[(r, t)] = model.NewBoolVar(f"assigned_r{r}_t{t}")

    # 3) A "completion time" variable for each task & robot
    finish_time = {}
    for r in range(num_robots):
        for t in range(num_tasks):
            finish_time[(r, t)] = model.NewIntVar(0, max_time, f"finish_r{r}_t{t}")

    # --- Constraints ---
    
    # (A) Each task is done exactly once (by exactly one robot)
    for t in range(num_tasks):
        model.Add(sum(assigned[(r, t)] for r in range(num_robots)) == 1)

    # (B) Relate start_time and finish_time:
    #     finish_time[r, t] = start_time[r, t] + task_duration(t) IF assigned[r, t] = 1
    #     otherwise, finish_time can be anything (but we can constrain logically).
    for r in range(num_robots):
        for t in range(num_tasks):
            duration_t = task_durations[t]
            # finish_time[r,t] >= start_time[r,t] + duration_t if assigned
            model.Add(finish_time[(r, t)] == start_time[(r, t)] + duration_t
                     ).OnlyEnforceIf(assigned[(r, t)])
            # If not assigned, we can fix them equal or do not care - to keep it simple, 
            # we can force finish_time == 0 or do no constraint, 
            # but we typically keep it flexible. 
            # We'll just skip an else-case for simplicity.

    # (C) Sequence/travel constraints for each robot:
    #     If robot r does tasks t1 and t2 in that order, we must have:
    #         start_time[r,t2] >= finish_time[r,t1] + travel_time(task_locations[t1], task_locations[t2])
    #     We can do a big pairwise disjunctive constraint:
    #         If x[r,t1] and x[r,t2] and t1 != t2, we define an ordering or no overlap.
    # 
    #     For simplicity, we do a naive "any two tasks the same robot does can't overlap in time" approach,
    #     plus the travel buffer. We do a pairwise approach for tasks t1 < t2:
    for r in range(num_robots):
        for t1 in range(num_tasks):
            for t2 in range(t1 + 1, num_tasks):
                # Travel time from location of t1 to t2
                travel_12 = distances[ task_locations[t1] ][ task_locations[t2] ]
                travel_21 = distances[ task_locations[t2] ][ task_locations[t1] ]

                # If the same robot does t1 and then t2:
                # start_time[r,t2] >= finish_time[r,t1] + travel_12
                c1 = model.Add(start_time[(r, t2)] >= finish_time[(r, t1)] + travel_12)
                c1.OnlyEnforceIf([assigned[(r, t1)], assigned[(r, t2)]])
                
                # If the same robot does t2 and then t1:
                # start_time[r,t1] >= finish_time[r,t2] + travel_21
                c2 = model.Add(start_time[(r, t1)] >= finish_time[(r, t2)] + travel_21)
                c2.OnlyEnforceIf([assigned[(r, t1)], assigned[(r, t2)]])

    # (D) Collision avoidance:
    #     We ensure that for any two robots r1 != r2, they never occupy the same location at the same time.
    #     In a discrete-time model, "occupying" the same location at time t means:
    #        - either robot is traveling through that location exactly at time t
    #        - or robot is executing a task at that location over an interval
    #
    #     A simple approach is:
    #        if assigned[r1, t1] and assigned[r2, t2], 
    #        the time window [start_time[r1,t1], finish_time[r1,t1]) for the location L(t1)
    #        must not overlap with [start_time[r2,t2], finish_time[r2,t2]) for L(t2) if L(t1) == L(t2).
    # 
    #     For traveling, we would also do pairwise checks, which can get more complicated. 
    #     Here, we'll just demonstrate the simplest location overlap check for tasks (ignoring collisions on paths).
    for t1 in range(num_tasks):
        for t2 in range(t1 + 1, num_tasks):
            loc1 = task_locations[t1]
            loc2 = task_locations[t2]
            # If tasks share the same location, we must ensure no overlap in times.
            if loc1 == loc2:
                for r1 in range(num_robots):
                    for r2 in range(r1 + 1, num_robots):
                        # We impose "no time overlap" if both tasks assigned and same location.
                        # Overlap occurs if start_time[r1,t1] < finish_time[r2,t2] AND 
                        #                  start_time[r2,t2] < finish_time[r1,t1].
                        # We'll forbid that overlap by imposing:
                        # finish_time[r1,t1] <= start_time[r2,t2] OR finish_time[r2,t2] <= start_time[r1,t1]
                        
                        no_overlap_1 = model.Add(finish_time[(r1, t1)] <= start_time[(r2, t2)])
                        no_overlap_2 = model.Add(finish_time[(r2, t2)] <= start_time[(r1, t1)])
                        
                        # Enforce them if assigned
                        # meaning at least one must be true
                        model.AddBoolOr([
                            no_overlap_1.ConstraintVar(), 
                            no_overlap_2.ConstraintVar()
                        ]).OnlyEnforceIf([
                            assigned[(r1,t1)],
                            assigned[(r2,t2)]
                        ])
    
    # (E) Objective: Minimize the makespan (time at which the last task finishes)
    #     We can track the finishing time of each assigned task and minimize the maximum among them.
    makespan = model.NewIntVar(0, max_time, 'makespan')
    for r in range(num_robots):
        for t in range(num_tasks):
            # makespan >= finish_time[r,t] if assigned
            model.Add(makespan >= finish_time[(r, t)]).OnlyEnforceIf(assigned[(r, t)])
    model.Minimize(makespan)

    # --- Solve ---
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print(f"Solution status = {solver.StatusName(status)}")
        print(f"Objective (makespan) = {solver.Value(makespan)}\n")
        for r in range(num_robots):
            print(f"--- Robot {r} ---")
            for t in range(num_tasks):
                if solver.Value(assigned[(r, t)]) == 1:
                    st = solver.Value(start_time[(r, t)])
                    ft = solver.Value(finish_time[(r, t)])
                    print(f"   Task {t}: start={st}, finish={ft}, location={task_locations[t]}")
            print("")
    else:
        print(f"No solution found. Status = {solver.StatusName(status)}")

if __name__ == "__main__":
    multi_robot_scheduling_example()
