import numpy as np

class Robot:
    def __init__(self):
        self.angles = np.array([np.radians(0), np.radians(90), np.radians(0), np.radians(0), np.radians(90), np.radians(0)])
        self.segmentLen = np.array([1, 1, 1, 1, 1, 1])
        self.position = np.zeros(6)

    def kinematics(self):
        DHparam = np.array([[self.angles[0],                    np.radians(-90),    5,      0],
                            [self.angles[1]-np.radians(90),     np.radians(0),      0,      5],
                            [self.angles[2]+np.radians(180),    np.radians(90),     0,      0],
                            [self.angles[3],                    np.radians(-90),    5,      0],
                            [self.angles[4],                    np.radians(90),     0,      0],
                            [self.angles[5],                    np.radians(0),      2.5,     0]])
        
        J = []
        for i in range(len(DHparam)):
            z = self.JointMatrix(DHparam[i])
            z[np.abs(z) < 1e-12] = 0
            print(z)
            print('\n')

            J.append(z)
        print('\n\n')
        a = np.dot(J[0], J[1])
        b = np.dot(a, J[2])
        c = np.dot(b, J[3])
        d = np.dot(c, J[4])
        e = np.dot(d, J[5])
        print(a, '\n\n', b, '\n\n', c, '\n\n', d, '\n\n', e)

    def JointMatrix(self, DHparam):
        DH = np.array([[np.cos(DHparam[0]), -np.sin(DHparam[0])*np.cos(DHparam[1]), np.sin(DHparam[0])*np.sin(DHparam[1]), DHparam[3]*np.cos(DHparam[0])],
                       [np.sin(DHparam[0]), np.cos(DHparam[0])*np.cos(DHparam[1]), -np.cos(DHparam[0])*np.sin(DHparam[1]), DHparam[3]*np.sin(DHparam[0])],
                       [0, np.sin(DHparam[1]), np.cos(DHparam[1]), DHparam[2]],
                       [0, 0, 0, 1]])
        return DH

def main():
    r = Robot()
    r.kinematics()


if __name__ == "__main__":
    main()