import numpy as np


# This is where you can build a decision tree for determining throttle, brake and steer 
# commands based on the output of the perception_step() function
def decision_step(Rover):

    # Implement conditionals to decide what to do given perception data
    # Here you're all set up with some basic functionality but you'll need to
    # improve on this decision tree to do a good job of navigating autonomously!

    def mean_without_outlier(arr):
        low = np.percentile(arr, 25)
        high = np.percentile(arr, 75)
        total = list()
        for c in arr:
            if c >= low and c <= high:
                total.append(c)
        return np.mean(total)

    # Example:
    # Check if we have vision data to make decisions with
    if Rover.nav_angles is not None:
        # Check for Rover.mode status
        if Rover.mode == 'forward': 
            # Check the extent of navigable terrain
            if len(Rover.nav_angles) >= Rover.stop_forward:  
                # If mode is forward, navigable terrain looks good 
                # and velocity is below max, then throttle 
                if Rover.vel < Rover.max_vel:
                    # Set throttle value to throttle setting
                    Rover.throttle = Rover.throttle_set
                else: # Else coast
                    Rover.throttle = 0
                Rover.brake = 0
                Rover.steer = np.clip(mean_without_outlier(Rover.nav_angles * 180/np.pi), -15, 15)
                if len(Rover.nav_angles) >= Rover.random_direction_angles:
                    if np.random.random() <= 0.2:
                        # print("get random direction because angle: ", len(Rover.nav_angles))
                        if Rover.steer >= 0:
                            Rover.steer = np.clip(np.random.normal(Rover.steer - 3, 3), -15, 15)
                        else:
                            Rover.steer = np.clip(np.random.normal(Rover.steer + 3, 3), -15, 15)
                

            # If there's a lack of navigable terrain pixels then go to 'stop' mode
            elif len(Rover.nav_angles) < Rover.stop_forward:
                if Rover.rock_angles is None or len(Rover.rock_angles) < Rover.rock_detected_angles:
                    # print("Smaller than stop forward")
                    # Set mode to "stop" and hit the brakes!
                    Rover.throttle = 0
                    # Set brake to stored brake value
                    Rover.brake = Rover.brake_set
                    Rover.steer = 0
                    Rover.mode = 'stop'

            if Rover.vel <= 0.2 and not Rover.is_stuck:
                if Rover.start_stuck_time is None:
                    # print("starting counting stuck time")
                    Rover.start_stuck_time = Rover.total_time
                if Rover.total_time - Rover.start_stuck_time >= Rover.stuck_turning_waiting_time:
                    # print("total time stuck", Rover.total_time - Rover.start_stuck_time)
                    Rover.is_stuck = True
            elif Rover.is_stuck and (Rover.throttle != 0 or Rover.brake != 0):
                if Rover.vel >= 0.2:
                    Rover.start_stuck_time = None
                    Rover.is_stuck = False
                else:
                    # print("stuck so i will turn")
                    Rover.brake = 0
                    if ((Rover.total_time - Rover.start_stuck_time) // Rover.stuck_turning_waiting_time) % 2 == 0:
                        Rover.throttle = Rover.throttle_set
                    else:
                        Rover.throttle = 0
                    Rover.steer = np.clip(-(Rover.steer + 5), -15, 15)
            else:
                Rover.is_stuck = False
                Rover.start_stuck_time = None

        # If we're already in "stop" mode then make different decisions
        elif Rover.mode == 'stop':
            # If we're in stop mode but still moving keep braking
            if Rover.vel > 0.2:
                # print("too fast in a stop mode so stop")
                Rover.throttle = 0
                Rover.brake = Rover.brake_set
                Rover.steer = 0
            # If we're not moving (vel < 0.2) then do something else
            elif Rover.vel <= 0.2:
                # Now we're stopped and we have vision data to see if there's a path forward
                if len(Rover.nav_angles) < Rover.go_forward:
                    # print("i am stopped and cannot go so i will look around ")
                    Rover.throttle = 0
                    # Release the brake to allow turning
                    Rover.brake = 0
                    # Turn range is +/- 15 degrees, when stopped the next line will induce 4-wheel turning
                    Rover.steer = -15
                # If we're stopped but see sufficient navigable terrain in front then go!
                if len(Rover.nav_angles) >= Rover.go_forward:
                    # print("let's go again because i can go now")
                    # Set throttle back to stored value
                    Rover.throttle = Rover.throttle_set
                    # Release the brake
                    Rover.brake = 0
                    # Set steer to mean angle
                    Rover.steer = np.clip(mean_without_outlier(Rover.nav_angles * 180/np.pi), -15, 15)
                    Rover.mode = 'forward'
                    

        # Just to make the rover do something 
        # even if no modifications have been made to the code
        else:
            # print("nothing to do so do something")
            Rover.throttle = 0
            Rover.steer = 15
            Rover.brake = 0
            
        # If in a state where want to pickup a rock send pickup command
        if Rover.near_sample:
            Rover.is_stuck = False
            Rover.start_stuck_time = None
            if Rover.vel == 0:
                # print("picking rock up")
                if not Rover.picking_up:
                    Rover.send_pickup = True
            else:
                # print("stop to pick rock")
                Rover.throttle = 0
                Rover.brake = Rover.brake_set
                Rover.steer = 0
                Rover.mode = 'stop'
        elif Rover.rock_angles is not None and len(Rover.rock_angles) >= Rover.rock_detected_angles and not Rover.is_stuck:
            target = np.clip(np.mean(Rover.rock_angles * 180/np.pi), -15, 15)
            Rover.steer = target
            # Rover.is_stuck = False
            # Rover.start_stuck_time = None
            if Rover.vel >= 1:
                # print("STOPPING for TO ROCKS")
                Rover.throttle = 0
                Rover.brake = Rover.brake_set
                Rover.mode = 'stop'
            else:
                # print("Going for rocks")
                Rover.throttle = Rover.throttle_set
                Rover.brake = 0
                Rover.mode = 'forward'
            # print("################# rock angles: ", len(Rover.rock_angles))

    
    return Rover

