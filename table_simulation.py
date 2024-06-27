# coding=utf-8
"""
    Interactive graphic interface for simulation of a collaborative task with a robot.
    User and the robot have to setting up a table correctly.

    (C) 2022 Sophia Corvaia, University of Palermo, Palermo, Italy
    Released under GNU Public License (GPL)
    Contacts: sophia.corvaia@unipa.it
"""
from PyQt5.QtWidgets import QWidget, QLabel, QApplication, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPixmap, QIcon
from random import shuffle, randint
from numpy import array
from numpy.linalg import norm
from pandas import read_csv
from sys import float_info, exit

# Global variables
list_obj = read_csv("./resources/data/table_points.csv")
list_obj = list_obj.set_index('Dish')
items = {}
centers = {}
occupied = {}
state = {}
item_under = None
item_over = None


def robot_move():
    """Pepper seleziona un pezzo non ancora sistemato (oppure sistema due pezzi).
    La funzione effettuerà una chiamata al modal model con una variabile settata ad AIUTO
    nel quale pepper dovrà fare i suoi ragionamenti su quale pezzo bisogna spostare"""
    # TODO: AGGIUSTARE. QUI IL ROBOT DOVRA' FARE LA SUA MOSSA
    missing = []
    pieces = []
    for value in occupied.values():
        pieces.append(value[0])
    for key in list(list_obj.index):
        if key in pieces:
            continue
        missing.append(key)
    if not missing:
        print("Non ho pezzi da spostare!")
        return
    # Tramite CLARION Pepper effettuerà la sua scelta.
    # O sposta un pezzo non ancora sistemato, oppure ne scambia due già piazzati ma ancora spostabili
    rand_index = randint(0, len(missing) - 1)
    label_choice = missing[rand_index]
    if label_choice in occupied.keys():
        # Potrebbe in questo caso scambiare i pezzi prima di spostarli
        print("Non posso spostare quel pezzo! Il suo posto è occupato!")
    items[label_choice].move_to_closer_point(False)


def stop_simulation():
    """Funzione che chiama per l'ultima volta il ciclo modal model in cui pepper tira le somme
    e ringrazia l'utente"""
    print('Simulation interrupted!')
    exit(0)


class DraggableItem(QLabel):
    """Extended class from PyQt5.QtWidgets.QLabel. This class provide a Draggable QLabel that represents
    dish item in table. User can drag and drop an item in table, setting its position"""

    def __init__(self, parent: QWidget, label: str, image: str, startPoint: QPoint, finalPoint: QPoint):
        """Constructor method.

        :param parent: PyQt5 QWidget parent that contain the item
        :type parent: QWidget
        :param label: Item name
        :type label: str
        :param image: Path for item's image file
        :type image: str
        :param startPoint: Item's initial position in table
        :type startPoint: QPoint
        :param finalPoint: Item's real and final position in table
        :type finalPoint: QPoint
        """
        super(QLabel, self).__init__(parent)
        self.mousePressPos = self.mouseMovePos = None
        self.startPosition = startPoint
        self.finalPosition = finalPoint
        self.currentPosition = QPoint(self.x(), self.y())
        self.label = label
        self.pixmap = QPixmap(image)

        self.attempt = 2
        self.blocked = False

        self.change_into_text()
        self.move(startPoint)

    def change_into_image(self):
        """Change label into image label
        """
        self.setPixmap(self.pixmap)
        self.setFixedHeight(self.pixmap.height())
        self.setFixedWidth(self.pixmap.width())
        self.setStyleSheet("""background-color: transparent;""")

    def change_into_text(self):
        """Change label into label with text
        """
        self.setText("      " + self.label)
        self.setFixedHeight(30)
        self.setFixedWidth(180)
        self.setStyleSheet("""background-color: white;""")

    def erase(self):
        """Remove previous occupied position from item, and it's state in table
        """
        global item_under
        global item_over
        if item_under == self.label:
            item_under = None
        elif item_over == self.label:
            item_over = None
        for key, value in occupied.items():
            if value[0] == self.label:
                del state[self.label]
                del occupied[key]
                return

    def mousePressEvent(self, event):
        if self.attempt == 0:
            self.blocked = True
            return
        if event.button() == Qt.LeftButton:
            self.mousePressPos = event.globalPos()
            self.mouseMovePos = event.globalPos()
            if self.attempt == 1:
                self.erase()

        super(DraggableItem, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.blocked:
            return
        if event.buttons() == Qt.LeftButton:
            # adjust offset from clicked point to origin of widget
            curr_pos = self.mapToGlobal(self.pos())
            global_pos = event.globalPos()
            diff = global_pos - self.mouseMovePos
            new_pos = self.mapFromGlobal(curr_pos + diff)
            # Enable movement in widget dimension parent
            parent_w = self.parent().width()
            obj_w = self.width()
            if new_pos.x() in range(0, parent_w + obj_w):
                self.move(new_pos)
                self.mouseMovePos = global_pos
                self.currentPosition = QPoint(self.x(), self.y())
                if self.x() in range(400 - obj_w, parent_w + obj_w):
                    self.change_into_image()
                else:
                    self.change_into_text()
                global item_under
                global item_over
                if item_under is not None and item_over is None:
                    items[item_under].stackUnder(self)
                elif item_under is not None and item_over is not None:
                    items[item_under].stackUnder(items[item_over])
                    items[item_over].stackUnder(self)

        super(DraggableItem, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.blocked:
            return
        if self.mousePressPos is not None:
            x_pos = self.currentPosition.x()
            if x_pos in range(0, 400 - self.width()):
                self.move(self.startPosition)
                self.erase()
                self.change_into_text()
            else:
                self.move_to_closer_point()

        # Start Modal Model Cycle
        # TODO: Runnare SUSAN con azioni. Dopo l'azione dell'utente c'è sempre quella del
        #  robot che valuta (ed eventualmente si incazza)

        # run(.....) robot_move()
        print('STATE: \n', state)
        print('OCCUPIED: \n', occupied)

        super(DraggableItem, self).mouseReleaseEvent(event)

    def move_to_closer_point(self, user=True):
        """Move item into currently closer point. The closer position will be occupied from item.
        The item state will be update.

        :param user: If the user is moving pieces or it's the robot
        :type user: bool
        """
        curr_key = None
        curr_value = None
        x_pos = (self.pixmap.width() // 2)
        y_pos = (self.pixmap.height() // 2)
        who = 'User'
        set_plates = ['plate', 'appetizer_plate']

        # Pepper is moving piece
        if not user:
            who = 'Robot'
            self.change_into_image()
            state[self.label] = [who, 'YES', 0]
            self.currentPosition = self.finalPosition
            self.move(self.finalPosition)
            curr_key = self.label
        else:
            obj_point = [self.currentPosition.x() + x_pos, self.currentPosition.y() + y_pos]
            min_dist = float_info.max
            for local_dish in list(list_obj.index):
                center = [centers[local_dish].x(), centers[local_dish].y()]
                curr = norm(array(center) - array(obj_point))
                if curr < min_dist:
                    min_dist = curr
                    curr_key = local_dish
                    curr_value = center
        # Check if closer point is occupied and move to piece's start position
        global item_under
        global item_over
        if (curr_key in occupied.keys() and curr_key not in set_plates) or \
                (curr_key in set_plates and item_under is not None and item_over is not None):
            self.change_into_text()
            self.move(self.startPosition)
            print(f"WARNING: {curr_key} position is already occupied!")
            return

        # Reduce attempt
        self.attempt = self.attempt - 1

        if (item_under == 'plate' and self.label == 'appetizer_plate' and
                curr_key in set_plates) or \
                (item_under is None and self.label == 'plate' and
                 curr_key in set_plates) or (curr_key == self.label and self.label not in set_plates):
            state[self.label] = [who, 'YES', self.attempt]
            self.currentPosition = self.finalPosition
            self.move(self.finalPosition)
        else:
            state[self.label] = [who, 'NO', self.attempt]
            self.currentPosition = QPoint(curr_value[0] - x_pos, curr_value[1] - y_pos)
            self.move(self.currentPosition)

        # Add occupied position
        if curr_key in set_plates and 'plate' in occupied.keys():
            occupied[self.label] = 'appetizer_plate'
        elif curr_key in set_plates and 'appetizer_plate' in occupied.keys():
            occupied[self.label] = 'plate'
        else:
            occupied[curr_key] = self.label

        if curr_key in set_plates and item_under is None:
            item_under = self.label
        elif curr_key in set_plates and item_under is not None:
            items[item_under].stackUnder(self)
            item_over = self.label


class Table(QWidget):
    """Extended class for PyQt5.QtWidgets.QWidget that represent Table in simulation.
    """

    def __init__(self):
        super(Table, self).__init__()
        self.setFixedSize(1200, 600)

        container = QWidget()
        container.setAttribute(Qt.WA_TransparentForMouseEvents)
        container.setStyleSheet("""
                background-image: url('./resources/images/dishes/tablecloth_empty.jpg')
            """)
        box = QHBoxLayout(self)
        box.setContentsMargins(0, 0, 0, 0)
        box.addWidget(container)
        container.raise_()


if __name__ == "__main__":
    app = QApplication([])
    window = QWidget()

    table = Table()
    layout = QHBoxLayout()
    layout.addWidget(table)
    window.setFixedSize(1200, 620)
    window.setLayout(layout)
    title = 'Help the robot to setting up the table!'
    window.setWindowTitle(title)
    window.setGeometry(500, 300, 1200, 600)

    # Shuffle starting item table
    temp_list = list(list_obj.index)
    shuffle(temp_list)

    # Initialize Dish items and add to table
    step = 15
    for label in temp_list:
        x_point = list_obj.loc[label]['X']
        y_point = list_obj.loc[label]['Y']
        start_point = QPoint(20, step)
        end_point = QPoint(x_point, y_point)
        image = './resources/images/dishes/' + label + '.png'
        dish = DraggableItem(table, label, image, start_point, end_point)
        items[label] = dish
        pixmap = QPixmap(image)
        centers[label] = QPoint(x_point + (pixmap.width() // 2), y_point + (pixmap.height() // 2))
        marker = QLabel(table)
        font = marker.font()
        font.setBold(True)
        marker.setFont(font)
        marker.setText('X')
        marker.move(centers[label])
        step = step + 45

    # Set Help Button
    help_btn = QPushButton(table)
    help_btn.setGeometry(220, 200, 150, 50)
    help_btn_text = '  Pass the turn'
    help_btn.setText(help_btn_text)
    help_btn.clicked.connect(robot_move)
    help_btn.setIcon(QIcon('./resources/images/robot_icon.png'))

    # Set stop simulation button
    stop_btn = QPushButton(table)
    stop_btn.setGeometry(220, 300, 150, 50)
    stop_btn_text = '  Stop'
    stop_btn.setText(stop_btn_text)
    stop_btn.clicked.connect(stop_simulation)
    stop_btn.setIcon(QIcon('./resources/images/stop_icon.png'))

    window.show()
    app.exec_()
