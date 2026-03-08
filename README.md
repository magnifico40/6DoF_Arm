🦾 Simple 6-DoF Robotic Arm Project in OpenGL


**Mechanical Design & Architecture**
* Custom CAD Components: Each segment of the arm was individually designed and is stored in Models3D directory
* Primitive-based geometry based on cylinders

**Motion & Kinematics**
* Forward Kinematics (FK):

  Self implemented kinematic rules to determine the End-Effector (gripper) pose based on joint state variables.

* Analytical Inverse Kinematics (IK):

   Self implemented inverse kinematics rules, to be optimized in future.

* Numerical Inverse Kinematics: 

  Imported numerical solution for determinig inverse kinematics rules.

  