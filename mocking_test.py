from unittest.mock import MagicMock, patch, Mock, PropertyMock


def create_mocks():
    mock_list = [MagicMock(), MagicMock(), MagicMock()]
    mock_list[0].move.side_effect = Mock(side_effect=ValueError)
    # p = PropertyMock(side_effect=ValueError)
    type(mock_list[1]).steps_per_um = PropertyMock(return_value=2)
    return mock_list


class Testing:

    def __init__(self):
        self.mock_list = self.get_list()

    def get_list(self):
        return [i for i in range(5)]

    def move(self, index):
        self.mock_list[index].move()


with patch.object(Testing, 'get_list', return_value=create_mocks()) as mock_get_list:
    test = Testing()

    for i in test.mock_list:
        try:
            i.steps_per_um = 5
            print(i.mock_calls)
        except ValueError:
            print('Found the Error!!')
    
    # print(i.connect.assert_called_once())