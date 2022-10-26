from unittest.mock import MagicMock, patch, Mock


def create_mocks():
    mock_list = [MagicMock(), MagicMock(), MagicMock()]
    mock_list[0].move.side_effect = Mock(side_effect=ValueError)
    return mock_list


class Testing:

    def __init__(self):
        self.mock_list = self.get_list()

    def get_list(self):
        return [i for i in range(5)]

    def move(self, index):
        self.mock_list[index].move()


with patch.object(Testing, 'get_list', return_value=create_mocks()):
    test = Testing()

    for i in test.mock_list:
        try:
            i.move()
        except ValueError:
            print('Found the Error!!')

    for i in test.mock_list:
        print(i.connect.assert_called_once())
    
    # print(i.connect.assert_called_once())