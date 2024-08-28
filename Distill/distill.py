from scipy.interpolate import CubicSpline, interp1d
import pandas as pd
import numpy as np
# import matplotlib.pyplot as plt

# path = "E:/Web/diagram/data/factory_data.xlsx"


class Distill:
    def __init__(self, entry, path, composition) -> None:
        # entry = (xf, xd, xw)
        self.xf, self.xd, self.xw = entry
        self.yd, self.yw = self.xd, self.xw

        # yf: vapor compostion at feed, yf_vapor: vapor compsition fromm interpolation
        self.yf, self.yf_vapor = None, None

        # reflux ratio
        self.R_min, self.R = None, None

        # diagram composition
        self.composition = composition

        # path is url to gg sheet file

        df = pd.read_excel(path, sheet_name=self.composition)

        # sort data for next calculation
        df = df.sort_values(by=["t"], ascending=False)

        self.liquid = df["x"].to_numpy()
        self.vapor = df["y"].to_numpy()
        self.temp = df["t"].to_numpy()

        # number of stage
        self.t_stage = None

        # coordiante of stair cases
        self.stair_x = None
        self.stair_y = None

    def cubic(self, x, y):
        f = CubicSpline(x, y, bc_type="natural")
        return f

    def interpolation(self, x, y):
        f = interp1d(x, y)
        return f

    def calculation(self):
        f = self.cubic(self.liquid, self.vapor)
        self.yf_vapor = np.around(f(self.xf), 3)
        self.R_min = np.around((self.xd - self.yf_vapor) / (self.yf_vapor - self.xf), 3)
        self.R = np.around(1.3 * self.R_min + 0.3, 3)
        self.yf = np.around(self.R / (self.R + 1) * self.xf + self.xd / (self.R + 1), 3)

        # line recitify and striping
        recitify = np.array([[self.xd, self.xf], [self.yd, self.yf]])
        stripping = np.array([[self.xw, self.xf], [self.yw, self.yf]])

        # stair line
        f_recitify = self.interpolation(recitify[0, :], recitify[1, :])
        f_stripping = self.interpolation(stripping[0, :], stripping[1, :])
        f1 = self.cubic(self.vapor, self.liquid)

        y1 = self.yd
        self.stair_x = np.array([self.xd])
        self.stair_y = np.array([])

        # main loop
        while True:
            self.stair_y = np.append(self.stair_y, [y1, y1])
            x1 = f1(y1)
            self.stair_x = np.append(self.stair_x, [x1, x1])
            if x1 >= self.xf:
                y1 = f_recitify(x1)
            elif x1 < self.xf and x1 > self.xw:
                y1 = f_stripping(x1)
            elif x1 < self.xw:
                self.stair_y = np.append(self.stair_y, x1)
                break

        self.t_stage = (self.stair_x.size - 1) / 2


# my_subtances = Distill((0.15, 0.8, 0.02), "ethanol-water")
# my_subtances.calculation()
# print(my_subtances.stair_x.tolist())
# print(my_subtances.stair_y.tolist())
# print(my_subtances.xf, my_subtances.yf)
