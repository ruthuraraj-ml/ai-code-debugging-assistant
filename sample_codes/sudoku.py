class Solution:
    def solveSudoku(self, board: List[List[str]]) -> None:
        """
        Do not return anything, modify board in-place instead.
        """
        current_row = [set() for num in range(9)]
        current_column = [set() for num in range(9)]
        current_box = [set() for num in range(9)]

        for index in range(81):
          row_index = index // 9
          column_index = index % 9
          box_row = row_index // 3
          box_col = column_index // 3
          box_id = (box_row, box_col)
          box_index = box_names.index(box_id)

          if board[row_index][column_index] != ".":
            current_row[row_index].add(board[row_index][column_index])
            current_column[column_index].add(board[row_index][column_index])
            current_box[box_index].add(board[row_index][column_index])

        def backtrack(index):
          
            if index == 81:
                return True

            row_index = index // 9
            column_index = index % 9
            box_row = row_index // 3
            box_col = column_index // 3
            box_id = (box_row, box_col)
            box_index = box_names.index(box_id)

            if board[row_index][column_index] != ".":
                return backtrack(index + 1)

            if board[row_index][column_index] == ".":
                for num in range(1, 10):
                    if str(num) not in current_row[row_index] and str(num) not in current_column[column_index] and str(num) not in current_box[box_index]:
                        board[row_index][column_index] = str(num)

                        current_row[row_index].add(str(num))
                        current_column[column_index].add(str(num))
                        current_box[box_index].add(str(num))

                        if backtrack(index + 1):
                            return True
                        board[row_index][column_index] = "."

                        current_row[row_index].remove(str(num))
                        current_column[column_index].remove(str(num))
                        current_box[box_index].remove(str(num))

        backtrack(0)