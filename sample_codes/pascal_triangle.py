def generate(self, numRows: int) -> List[List[int]]:
        if numRows == 1:
            return [[1]]
        if numRows == 2:
            return [[1], [1, 1]]
        triangle = [[1], [1, 2]]
        rows = 3
        while rows <= numRows:
            current_row = []
            for i in range(len(triangle[rows - 2]) - 1):
                current_row.append(triangle[-1][i] + triangle[-1][i + 1])
            current_row = [1] + current_row + [1]
            triangle.append(current_row)
            rows += 1

        return triangle