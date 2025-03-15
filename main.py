from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QTableWidget, QWidget,
                               QTableWidgetItem, QHBoxLayout, QLabel, QLineEdit, QPushButton,
                               QDialog, QFormLayout, QDateEdit, QComboBox, QMessageBox, QDoubleSpinBox,
                               QSizePolicy, QHeaderView)
from PySide6.QtCore import QDate, Qt, QSize, Signal
from PySide6.QtGui import QIcon
from db import get_session, Animal, Species, Enclosure, Employee, HealthRecord, AnimalFeed, Feed, Offspring

# Кастомный класс для кнопки с иконкой "+"
class CustomButtonWidget(QWidget):
    clicked = Signal(str)
    plus_clicked = Signal(str)

    def __init__(self, text, plus_icon_path, plus_icon_size, parent=None):
        super().__init__(parent)
        self.setFixedSize(298, 48)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.main_button = QPushButton(text)
        self.main_button.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #636363;
                border-radius: 5px;
                border: 1px solid #ECECEC;
                padding: 5px 10px;
                font-size: 14px;
                text-align: left;
                padding-right: 50px;
                position: relative;
            }
            QPushButton:hover {
                background-color: #C7E8FF;
                color: #636363;
            }
        """)
        self.main_button.clicked.connect(lambda: self.clicked.emit(text))

        self.plus_button = QPushButton(self.main_button)
        self.plus_button.setIcon(QIcon(plus_icon_path))
        self.plus_button.setIconSize(plus_icon_size)
        self.plus_button.setFixedSize(QSize(30, 30))
        self.plus_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                qproperty-iconSize: 24px;
                padding: 3px;
            }
            QPushButton:hover {
                background-color: #C7E8FF;
                border-radius: 10px;
            }
        """)
        self.plus_button.move(298 - 30 - 10, (48 - 30) // 2)
        self.plus_button.clicked.connect(lambda: self.plus_clicked.emit(text + "_add"))

        self.layout.addWidget(self.main_button)
        self.main_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

    def resizeEvent(self, event):
        self.setFixedSize(298, 48)
        self.plus_button.move(298 - 30 - 10, (48 - 30) // 2)
        super().resizeEvent(event)

    def set_active(self, active):
        if active:
            self.main_button.setStyleSheet("""
                QPushButton {
                    background-color: #C7E8FF;
                    color: #636363;
                    border-radius: 5px;
                    border: 1px solid #ECECEC;
                    padding: 5px 10px;
                    font-size: 14px;
                    text-align: left;
                    padding-right: 50px;
                    position: relative;
                }
                QPushButton:hover {
                    background-color: #C7E8FF;
                    color: #636363;
                }
            """)
        else:
            self.main_button.setStyleSheet("""
                QPushButton {
                    background-color: #FFFFFF;
                    color: #636363;
                    border-radius: 5px;
                    border: 1px solid #ECECEC;
                    padding: 5px 10px;
                    font-size: 14px;
                    text-align: left;
                    padding-right: 50px;
                    position: relative;
                }
                QPushButton:hover {
                    background-color: #C7E8FF;
                    color: #636363;
                }
            """)

# Базовый диалог
class BaseDialog(QDialog):
    def __init__(self, parent=None, title=""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(400)
        self.layout = QFormLayout(self)
        self.layout.setSpacing(10)

        buttons_layout = QHBoxLayout()
        save_button = QPushButton("Сохранить")
        save_button.setObjectName("save")
        cancel_button = QPushButton("Отмена")
        cancel_button.setObjectName("cancel")
        
        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(cancel_button)
        self.layout.addRow(buttons_layout)

# Диалог для добавления вида
class SpeciesDialog(BaseDialog):
    def __init__(self, parent=None, species=None):
        super().__init__(parent, "Добавить вид")
        self.name = QLineEdit()
        self.layout.addRow("Название вида:", self.name)
        if species:
            self.name.setText(species.name)

# Диалог для животных
class AnimalDialog(BaseDialog):
    def __init__(self, parent=None, animal=None):
        super().__init__(parent, "Животное")
        self.name = QLineEdit()
        self.species = QComboBox()
        self.enclosure = QComboBox()
        self.date_of_birth = QDateEdit()
        self.date_of_birth.setCalendarPopup(True)
        self.date_of_birth.setDate(QDate.currentDate())
        self.date_of_arrival = QDateEdit()
        self.date_of_arrival.setCalendarPopup(True)
        self.date_of_arrival.setDate(QDate.currentDate())
        self.sex = QComboBox()
        self.sex.addItems(["Male", "Female"])

        self.load_species()
        self.load_enclosures()

        species_layout = QHBoxLayout()
        species_layout.addWidget(self.species)
        add_species_button = QPushButton("Добавить вид")
        add_species_button.setObjectName("add_species_button")
        add_species_button.setIconSize(QSize(24, 24))
        add_species_button.clicked.connect(self.add_species)
        species_layout.addWidget(add_species_button)

        self.layout.addRow("Имя:", self.name)
        self.layout.addRow("Вид:", species_layout)
        self.layout.addRow("Вольер:", self.enclosure)
        self.layout.addRow("Дата рождения:", self.date_of_birth)
        self.layout.addRow("Дата прибытия:", self.date_of_arrival)
        self.layout.addRow("Пол:", self.sex)

        if animal:
            self.name.setText(animal.name)
            self.species.setCurrentIndex(self.species.findData(animal.species_id))
            self.enclosure.setCurrentIndex(self.enclosure.findData(animal.enclosure_id))
            self.date_of_birth.setDate(QDate.fromString(str(animal.date_of_birth), "yyyy-MM-dd"))
            self.date_of_arrival.setDate(QDate.fromString(str(animal.date_of_arrival), "yyyy-MM-dd"))
            self.sex.setCurrentText(animal.sex)

    def load_species(self):
        self.species.clear()
        with get_session() as session:
            species_list = session.query(Species).all()
            if not species_list:
                QMessageBox.warning(self, "Предупреждение", "Нет видов животных. Добавьте виды.")
            for sp in species_list:
                self.species.addItem(sp.name, sp.id)

    def load_enclosures(self):
        self.enclosure.clear()
        with get_session() as session:
            enclosures = session.query(Enclosure).all()
            if not enclosures:
                QMessageBox.warning(self, "Предупреждение", "Нет вольеров. Добавьте вольеры.")
            for enc in enclosures:
                self.enclosure.addItem(enc.name, enc.id)

    def add_species(self):
        species_dialog = SpeciesDialog(self)
        if species_dialog.exec():
            with get_session() as session:
                try:
                    new_species = Species(name=species_dialog.name.text())
                    session.add(new_species)
                    session.commit()
                    QMessageBox.information(self, "Успех", "Новый вид успешно добавлен!")
                    self.load_species()
                    self.species.setCurrentIndex(self.species.findData(new_species.id))
                except Exception as e:
                    session.rollback()
                    QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении вида: {str(e)}")

# Диалог для сотрудников
class EmployeeDialog(BaseDialog):
    def __init__(self, parent=None, employee=None):
        super().__init__(parent, "Сотрудник")
        self.name = QLineEdit()
        self.position = QLineEdit()
        self.phone = QLineEdit()
        self.hire_date = QDateEdit()
        self.hire_date.setCalendarPopup(True)
        self.hire_date.setDate(QDate.currentDate())

        self.layout.addRow("Имя:", self.name)
        self.layout.addRow("Должность:", self.position)
        self.layout.addRow("Телефон:", self.phone)
        self.layout.addRow("Дата найма:", self.hire_date)

        if employee:
            self.name.setText(employee.name)
            self.position.setText(employee.position)
            self.phone.setText(employee.phone)
            self.hire_date.setDate(QDate.fromString(str(employee.hire_date), "yyyy-MM-dd"))

# Диалог для вольеров
class EnclosureDialog(BaseDialog):
    def __init__(self, parent=None, enclosure=None):
        super().__init__(parent, "Вольер")
        self.name = QLineEdit()
        self.size = QDoubleSpinBox()
        self.size.setRange(0, 10000)
        self.location = QLineEdit()
        self.description = QLineEdit()

        self.layout.addRow("Название:", self.name)
        self.layout.addRow("Размер (м²):", self.size)
        self.layout.addRow("Местоположение:", self.location)
        self.layout.addRow("Описание:", self.description)

        if enclosure:
            self.name.setText(enclosure.name)
            self.size.setValue(enclosure.size)
            self.location.setText(enclosure.location)
            self.description.setText(enclosure.description)

# Диалог для кормления
class AnimalFeedDialog(BaseDialog):
    def __init__(self, parent=None, animal_feed=None):
        super().__init__(parent, "Кормление")
        self.animal = QComboBox()
        self.feed = QComboBox()
        self.daily_amount = QDoubleSpinBox()
        self.daily_amount.setRange(0, 1000)

        with get_session() as session:
            animals = session.query(Animal).all()
            if not animals:
                QMessageBox.warning(self, "Предупреждение", "Нет животных. Добавьте животных.")
            for a in animals:
                self.animal.addItem(a.name, a.id)
            feeds = session.query(Feed).all()
            if not feeds:
                QMessageBox.warning(self, "Предупреждение", "Нет кормов. Добавьте корма.")
            for f in feeds:
                self.feed.addItem(f.name, f.id)

        self.layout.addRow("Животное:", self.animal)
        self.layout.addRow("Корм:", self.feed)
        self.layout.addRow("Суточная норма (кг):", self.daily_amount)

        if animal_feed:
            self.animal.setCurrentIndex(self.animal.findData(animal_feed.animal_id))
            self.feed.setCurrentIndex(self.feed.findData(animal_feed.feed_id))
            self.daily_amount.setValue(animal_feed.daily_amount)

# Диалог для медицинских записей
class HealthRecordDialog(BaseDialog):
    def __init__(self, parent=None, health_record=None):
        super().__init__(parent, "Медицинская запись")
        self.animal = QComboBox()
        self.checkup_date = QDateEdit()
        self.checkup_date.setCalendarPopup(True)
        self.checkup_date.setDate(QDate.currentDate())
        self.notes = QLineEdit()

        with get_session() as session:
            animals = session.query(Animal).all()
            if not animals:
                QMessageBox.warning(self, "Предупреждение", "Нет животных. Добавьте животных.")
            for a in animals:
                self.animal.addItem(a.name, a.id)

        self.layout.addRow("Животное:", self.animal)
        self.layout.addRow("Дата осмотра:", self.checkup_date)
        self.layout.addRow("Заметки:", self.notes)

        if health_record:
            self.animal.setCurrentIndex(self.animal.findData(health_record.animal_id))
            self.checkup_date.setDate(QDate.fromString(str(health_record.checkup_date), "yyyy-MM-dd"))
            self.notes.setText(health_record.notes)

# Главное окно
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Управление зоопарком")
        self.setGeometry(200, 200, 1024, 768)
        self.setMinimumSize(1024, 768)
        self.setup_ui()
        self.apply_styles()
        self.show_animals()
        self.current_table = self.animals_table
        self.animals_table.show()
        self.set_active_button("Животные")

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #F5F6FF; font-family: 'Regular', 'Inter'; }
            QLabel#logo { padding: 10px; }
            QLineEdit {
                background-color: #FFFFFF;
                border: 1px solid #ECECEC;
                border-radius: 5px;
                padding: 10px 15px;
                font-size: 14px;
            }
            #save, #cancel { text-align: center; }
            QPushButton {
                background-color: #FFFFFF;
                color: #636363;
                border-radius: 5px;
                border: 1px solid #ECECEC;
                padding: 5px 10px;
                font-size: 14px;
                text-align: left;
            }
            QPushButton#report_button {
                background-color: #FFFFFF;
                color: #636363;
                border-radius: 5px;
                border: 1px solid #ECECEC;
                padding: 5px 10px;
                font-size: 14px;
                text-align: center;
            }
            QPushButton#report_button:hover {
                background-color: #C7E8FF;
                color: #636363;
                border: 1px solid #ECECEC;
            }
            QPushButton#delete_button {
                background-color: #FFC1C1;
                color: #636363;
                border-radius: 5px;
                border: 1px solid #ECECEC;
                text-align: center;
            }
            QPushButton#delete_button:hover {
                background-color: #FF9999;
                color: #FFFFFF;
                border: 1px solid #ECECEC;
            }
            QPushButton#add_button {
                background-color: #5FFFD2;
                color: #636363;
                border-radius: 5px;
                border: 1px solid #ECECEC;
                text-align: center;
            }
            QPushButton#add_button:hover {
                background-color: #00E6A8;
                color: #FFFFFF;
                border: 1px solid #ECECEC;
            }
            QPushButton#add_species_button {
                background-color: #FFFFFF;
                color: #636363;
                border: 1px solid #ECECEC;
                border-radius: 5px;
                padding: 5px 10px;
                font-size: 14px;
            }
            QPushButton#add_species_button:hover { 
                background-color: #C7E8FF; 
                color: #636363; 
            }
            QPushButton:hover { 
                background-color: #C7E8FF; 
                color: #636363; 
            }
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #ECECEC;
                border-radius: 5px;
                font-size: 12px;
                alternate-background-color: #FFFFFF;
            }
            QTableWidget::item { 
                padding: 5px; 
            }
            QHeaderView::section {
                background-color: #C7E8FF;
                color: #636363;
                padding: 5px;
                font-size: 12px;
            }
            QHeaderView { 
                background-color: rgba(0,0,0,0); 
            }
            QDialog {
                background-color: #F5F6FF;
                border: 1px solid #ECECEC;
                border-radius: 10px;
            }
            QComboBox {
                background-color: #FFFFFF;
                border: 1px solid #ECECEC;
                border-radius: 5px;
                padding: 5px 10px;
                font-size: 14px;
                color: #636363;
            }
            QComboBox:hover {
                background-color: #C7E8FF;
            }
            QComboBox QAbstractItemView {
                color: #636363;
                background-color: #FFFFFF;
                selection-background-color: #C7E8FF;
            }
        """)

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        logo = QLabel()
        logo.setObjectName("logo")
        logo_icon = QIcon("logo.svg")
        logo_pixmap = logo_icon.pixmap(QSize(120, 120))
        logo.setPixmap(logo_pixmap)
        left_layout.addWidget(logo)

        self.buttons = []
        button_configs = [
            ("Животные", "plus.svg", QSize(24, 24)),
            ("Сотрудники", "plus.svg", QSize(24, 24)),
            ("Вольеры", "plus.svg", QSize(24, 24)),
            ("Кормление", "plus.svg", QSize(24, 24)),
            ("Медицина", "plus.svg", QSize(24, 24)),
        ]

        for text, plus_icon_path, plus_icon_size in button_configs:
            button_widget = CustomButtonWidget(text, plus_icon_path, plus_icon_size)
            button_widget.setFixedSize(298, 48)
            button_widget.clicked.connect(self.show_section)
            button_widget.plus_clicked.connect(self.add_item_from_plus)
            self.buttons.append(button_widget)
            left_layout.addWidget(button_widget)

        # Добавляем дополнительный отступ перед элементами отчёта
        left_layout.addSpacing(50)

        # Добавляем контейнер для отчётов внизу левой панели
        report_panel = QWidget()
        report_layout = QVBoxLayout(report_panel)  # Вертикальный layout для выпадающего списка и кнопки
        report_layout.setContentsMargins(0, 0, 0, 0)

        self.report_combo = QComboBox()
        self.report_combo.setFixedSize(298, 48)
        self.report_combo.addItems([
            "Отчёт по животным",
            "Отчёт по сотрудникам",
            "Отчёт по вольерам",
            "Отчёт по кормлению",
            "Отчёт по медицинским записям"
        ])
        self.report_combo.setCurrentText("Отчёт по животным")

        self.report_button = QPushButton("Сгенерировать")
        self.report_button.setObjectName("report_button")
        self.report_button.setFixedSize(298, 48)
        self.report_button.clicked.connect(self.generate_report)

        report_layout.addWidget(self.report_combo)
        report_layout.addWidget(self.report_button)
        left_layout.addWidget(report_panel)

        left_layout.addStretch()
        main_layout.addWidget(left_panel)
        main_layout.setStretch(0, 1)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск")
        right_layout.addWidget(self.search_input)

        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(0, 5, 0, 0)

        self.delete_button = QPushButton("Удалить")
        self.delete_button.setObjectName("delete_button")
        self.delete_button.setFixedHeight(38)
        self.delete_button.clicked.connect(self.delete_item)

        self.add_button = QPushButton("Добавить")
        self.add_button.setObjectName("add_button")
        self.add_button.setFixedHeight(38)
        self.add_button.clicked.connect(self.add_item)

        buttons_layout.addWidget(self.delete_button)
        buttons_layout.addWidget(self.add_button)
        right_layout.addWidget(buttons_widget)

        self.animals_table = QTableWidget()
        self.employees_table = QTableWidget()
        self.enclosures_table = QTableWidget()
        self.feeding_table = QTableWidget()
        self.health_table = QTableWidget()
        for table in [self.animals_table, self.employees_table, self.enclosures_table,
                      self.feeding_table, self.health_table]:
            table.setAlternatingRowColors(True)
            table.setEditTriggers(QTableWidget.NoEditTriggers)
            table.doubleClicked.connect(self.edit_item_on_double_click)
            right_layout.addWidget(table)

        self.search_input.textChanged.connect(self.search_items)

        main_layout.addWidget(right_panel)
        main_layout.setStretch(1, 2)

        self.hide_all_tables()
        self.current_table = None

    def generate_report(self):
        report_type = self.report_combo.currentText()
        if not report_type:  # Проверяем, выбрано ли что-то
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите тип отчёта.")
            return

        with get_session() as session:
            if report_type == "Отчёт по животным":
                animals = session.query(Animal).all()
                report = "Отчёт по животным:\n"
                for animal in animals:
                    report += (f"Имя: {animal.name}, Вид: {animal.fk_species.name if animal.fk_species else 'Не указан'}, "
                               f"Вольер: {animal.fk_enclosure.name if animal.fk_enclosure else 'Не указан'}\n")
            elif report_type == "Отчёт по сотрудникам":
                employees = session.query(Employee).all()
                report = "Отчёт по сотрудникам:\n"
                for emp in employees:
                    report += f"Имя: {emp.name}, Должность: {emp.position}, Телефон: {emp.phone}\n"
            elif report_type == "Отчёт по вольерам":
                enclosures = session.query(Enclosure).all()
                report = "Отчёт по вольерам:\n"
                for enc in enclosures:
                    report += f"Название: {enc.name}, Размер: {enc.size} м², Местоположение: {enc.location}\n"
            elif report_type == "Отчёт по кормлению":
                feedings = session.query(AnimalFeed).all()
                report = "Отчёт по кормлению:\n"
                for feed in feedings:
                    report += (f"Животное: {feed.fk_animal.name if feed.fk_animal else 'Не указано'}, "
                               f"Корм: {feed.fk_feed.name if feed.fk_feed else 'Не указано'}, "
                               f"Суточная норма: {feed.daily_amount} кг\n")
            elif report_type == "Отчёт по медицинским записям":
                health_records = session.query(HealthRecord).all()
                report = "Отчёт по медицинским записям:\n"
                for record in health_records:
                    report += (f"Животное: {record.fk_animal.name if record.fk_animal else 'Не указано'}, "
                               f"Дата осмотра: {record.checkup_date}, Заметки: {record.notes}\n")
            else:
                report = "Неизвестный тип отчёта."

        # Выводим отчёт в диалоговом окне
        QMessageBox.information(self, "Отчёт", report)

    def show_section(self, section):
        self.hide_all_tables()
        if section == "Животные":
            self.current_table = self.animals_table
            self.show_animals()
        elif section == "Сотрудники":
            self.current_table = self.employees_table
            self.show_employees()
        elif section == "Вольеры":
            self.current_table = self.enclosures_table
            self.show_enclosures()
        elif section == "Кормление":
            self.current_table = self.feeding_table
            self.show_feeding()
        elif section == "Медицина":
            self.current_table = self.health_table
            self.show_health()
        self.current_table.show()
        self.set_active_button(section)

    def set_active_button(self, active_section):
        for button_widget in self.buttons:
            button_widget.set_active(False)
        for button_widget in self.buttons:
            if button_widget.main_button.text() == active_section:
                button_widget.set_active(True)
                break

    def add_item_from_plus(self, action):
        if action.endswith("_add"):
            section = action[:-4]
            if section == "Животные":
                self.current_table = self.animals_table
                dialog = AnimalDialog(self)
                if dialog.exec():
                    with get_session() as session:
                        new_animal = Animal(
                            name=dialog.name.text(),
                            species_id=dialog.species.currentData(),
                            enclosure_id=dialog.enclosure.currentData(),
                            date_of_birth=dialog.date_of_birth.date().toPython(),
                            date_of_arrival=dialog.date_of_arrival.date().toPython(),
                            sex=dialog.sex.currentText()
                        )
                        session.add(new_animal)
                        session.commit()
                        self.show_animals()
            elif section == "Сотрудники":
                self.current_table = self.employees_table
                dialog = EmployeeDialog(self)
                if dialog.exec():
                    with get_session() as session:
                        new_employee = Employee(
                            name=dialog.name.text(),
                            position=dialog.position.text(),
                            phone=dialog.phone.text(),
                            hire_date=dialog.hire_date.date().toPython()
                        )
                        session.add(new_employee)
                        session.commit()
                        self.show_employees()
            elif section == "Вольеры":
                self.current_table = self.enclosures_table
                dialog = EnclosureDialog(self)
                if dialog.exec():
                    with get_session() as session:
                        new_enclosure = Enclosure(
                            name=dialog.name.text(),
                            size=dialog.size.value(),
                            location=dialog.location.text(),
                            description=dialog.description.text()
                        )
                        session.add(new_enclosure)
                        session.commit()
                        self.show_enclosures()
            elif section == "Кормление":
                self.current_table = self.feeding_table
                dialog = AnimalFeedDialog(self)
                if dialog.exec():
                    with get_session() as session:
                        new_feeding = AnimalFeed(
                            animal_id=dialog.animal.currentData(),
                            feed_id=dialog.feed.currentData(),
                            daily_amount=dialog.daily_amount.value()
                        )
                        session.add(new_feeding)
                        session.commit()
                        self.show_feeding()
            elif section == "Медицина":
                self.current_table = self.health_table
                dialog = HealthRecordDialog(self)
                if dialog.exec():
                    with get_session() as session:
                        new_health = HealthRecord(
                            animal_id=dialog.animal.currentData(),
                            checkup_date=dialog.checkup_date.date().toPython(),
                            notes=dialog.notes.text()
                        )
                        session.add(new_health)
                        session.commit()
                        self.show_health()

    def load_data(self, session, model, table_widget, headers, data_function):
        self.current_items = session.query(model).all()
        table_widget.setRowCount(len(self.current_items))
        table_widget.setColumnCount(len(headers))
        table_widget.setHorizontalHeaderLabels(headers)
        for row, item in enumerate(self.current_items):
            for col, value in enumerate(data_function(item)):
                table_widget.setItem(row, col, QTableWidgetItem(str(value)))
        table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def show_animals(self):
        with get_session() as session:
            headers = ["Имя", "Вид", "Вольер", "Дата рождения", "Дата прибытия", "Пол"]
            def get_animal_data(animal):
                return [
                    animal.name,
                    animal.fk_species.name if animal.fk_species else "",
                    animal.fk_enclosure.name if animal.fk_enclosure else "",
                    animal.date_of_birth,
                    animal.date_of_arrival,
                    animal.sex
                ]
            self.load_data(session, Animal, self.animals_table, headers, get_animal_data)
            self.set_active_button("Животные")

    def show_employees(self):
        with get_session() as session:
            headers = ["Имя", "Должность", "Телефон", "Дата найма"]
            def get_employee_data(employee):
                return [employee.name, employee.position, employee.phone, employee.hire_date]
            self.load_data(session, Employee, self.employees_table, headers, get_employee_data)
            self.set_active_button("Сотрудники")

    def show_enclosures(self):
        with get_session() as session:
            headers = ["Название", "Размер (m²)", "Местоположение", "Описание"]
            def get_enclosure_data(enclosure):
                return [enclosure.name, enclosure.size, enclosure.location, enclosure.description]
            self.load_data(session, Enclosure, self.enclosures_table, headers, get_enclosure_data)
            self.set_active_button("Вольеры")

    def show_feeding(self):
        with get_session() as session:
            headers = ["Животное", "Корм", "Суточная норма (кг)"]
            def get_feeding_data(animal_feed):
                return [
                    animal_feed.fk_animal.name if animal_feed.fk_animal else "",
                    animal_feed.fk_feed.name if animal_feed.fk_feed else "",
                    animal_feed.daily_amount
                ]
            self.load_data(session, AnimalFeed, self.feeding_table, headers, get_feeding_data)
            self.set_active_button("Кормление")

    def show_health(self):
        with get_session() as session:
            headers = ["Животное", "Дата осмотра", "Заметки"]
            def get_health_data(health_record):
                return [
                    health_record.fk_animal.name if health_record.fk_animal else "",
                    health_record.checkup_date,
                    health_record.notes
                ]
            self.load_data(session, HealthRecord, self.health_table, headers, get_health_data)
            self.set_active_button("Медицина")

    def hide_all_tables(self):
        for table in [self.animals_table, self.employees_table, self.enclosures_table,
                      self.feeding_table, self.health_table]:
            table.hide()

    def add_item(self):
        with get_session() as session:
            try:
                if self.current_table == self.animals_table:
                    dialog = AnimalDialog(self)
                    if dialog.exec():
                        new_animal = Animal(
                            name=dialog.name.text(),
                            species_id=dialog.species.currentData(),
                            enclosure_id=dialog.enclosure.currentData(),
                            date_of_birth=dialog.date_of_birth.date().toPython(),
                            date_of_arrival=dialog.date_of_arrival.date().toPython(),
                            sex=dialog.sex.currentText()
                        )
                        session.add(new_animal)
                        session.commit()
                        self.show_animals()
                elif self.current_table == self.employees_table:
                    dialog = EmployeeDialog(self)
                    if dialog.exec():
                        new_employee = Employee(
                            name=dialog.name.text(),
                            position=dialog.position.text(),
                            phone=dialog.phone.text(),
                            hire_date=dialog.hire_date.date().toPython()
                        )
                        session.add(new_employee)
                        session.commit()
                        self.show_employees()
                elif self.current_table == self.enclosures_table:
                    dialog = EnclosureDialog(self)
                    if dialog.exec():
                        new_enclosure = Enclosure(
                            name=dialog.name.text(),
                            size=dialog.size.value(),
                            location=dialog.location.text(),
                            description=dialog.description.text()
                        )
                        session.add(new_enclosure)
                        session.commit()
                        self.show_enclosures()
                elif self.current_table == self.feeding_table:
                    dialog = AnimalFeedDialog(self)
                    if dialog.exec():
                        new_feeding = AnimalFeed(
                            animal_id=dialog.animal.currentData(),
                            feed_id=dialog.feed.currentData(),
                            daily_amount=dialog.daily_amount.value()
                        )
                        session.add(new_feeding)
                        session.commit()
                        self.show_feeding()
                elif self.current_table == self.health_table:
                    dialog = HealthRecordDialog(self)
                    if dialog.exec():
                        new_health = HealthRecord(
                            animal_id=dialog.animal.currentData(),
                            checkup_date=dialog.checkup_date.date().toPython(),
                            notes=dialog.notes.text()
                        )
                        session.add(new_health)
                        session.commit()
                        self.show_health()
            except Exception as e:
                session.rollback()
                QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении: {str(e)}")

    def edit_item_on_double_click(self, index):
        if not self.current_table:
            return

        current_row = index.row()
        if current_row < 0:
            return

        with get_session() as session:
            try:
                if self.current_table == self.animals_table:
                    self.current_items = session.query(Animal).all()
                    if current_row >= len(self.current_items):
                        return
                    item_id = self.current_items[current_row].id
                    item = session.query(Animal).filter_by(id=item_id).first()
                    if not item:
                        return
                    dialog = AnimalDialog(self, item)
                    if dialog.exec():
                        item.name = dialog.name.text()
                        item.species_id = dialog.species.currentData()
                        item.enclosure_id = dialog.enclosure.currentData()
                        item.date_of_birth = dialog.date_of_birth.date().toPython()
                        item.date_of_arrival = dialog.date_of_arrival.date().toPython()
                        item.sex = dialog.sex.currentText()
                        session.merge(item)
                        session.commit()
                        self.show_animals()
                elif self.current_table == self.employees_table:
                    self.current_items = session.query(Employee).all()
                    if current_row >= len(self.current_items):
                        return
                    item_id = self.current_items[current_row].id
                    item = session.query(Employee).filter_by(id=item_id).first()
                    if not item:
                        return
                    dialog = EmployeeDialog(self, item)
                    if dialog.exec():
                        item.name = dialog.name.text()
                        item.position = dialog.position.text()
                        item.phone = dialog.phone.text()
                        item.hire_date = dialog.hire_date.date().toPython()
                        session.merge(item)
                        session.commit()
                        self.show_employees()
                elif self.current_table == self.enclosures_table:
                    self.current_items = session.query(Enclosure).all()
                    if current_row >= len(self.current_items):
                        return
                    item_id = self.current_items[current_row].id
                    item = session.query(Enclosure).filter_by(id=item_id).first()
                    if not item:
                        return
                    dialog = EnclosureDialog(self, item)
                    if dialog.exec():
                        item.name = dialog.name.text()
                        item.size = dialog.size.value()
                        item.location = dialog.location.text()
                        item.description = dialog.description.text()
                        session.merge(item)
                        session.commit()
                        self.show_enclosures()
                elif self.current_table == self.feeding_table:
                    self.current_items = session.query(AnimalFeed).all()
                    if current_row >= len(self.current_items):
                        return
                    item_id = self.current_items[current_row].id
                    item = session.query(AnimalFeed).filter_by(id=item_id).first()
                    if not item:
                        return
                    dialog = AnimalFeedDialog(self, item)
                    if dialog.exec():
                        item.animal_id = dialog.animal.currentData()
                        item.feed_id = dialog.feed.currentData()
                        item.daily_amount = dialog.daily_amount.value()
                        session.merge(item)
                        session.commit()
                        self.show_feeding()
                elif self.current_table == self.health_table:
                    self.current_items = session.query(HealthRecord).all()
                    if current_row >= len(self.current_items):
                        return
                    item_id = self.current_items[current_row].id
                    item = session.query(HealthRecord).filter_by(id=item_id).first()
                    if not item:
                        return
                    dialog = HealthRecordDialog(self, item)
                    if dialog.exec():
                        item.animal_id = dialog.animal.currentData()
                        item.checkup_date = dialog.checkup_date.date().toPython()
                        item.notes = dialog.notes.text()
                        session.merge(item)
                        session.commit()
                        self.show_health()
                QMessageBox.information(self, "Успех", "Данные успешно отредактированы!")
            except Exception as e:
                session.rollback()
                QMessageBox.critical(self, "Ошибка", f"Ошибка при редактировании: {str(e)}")

    def delete_item(self):
        if not self.current_table:
            QMessageBox.warning(self, "Ошибка", "Выберите таблицу для удаления")
            return

        current_row = self.current_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите строку для удаления")
            return

        reply = QMessageBox.question(self, "Подтверждение", "Вы уверены, что хотите удалить эту запись?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return

        with get_session() as session:
            try:
                if self.current_table == self.animals_table:
                    self.current_items = session.query(Animal).all()
                    if current_row >= len(self.current_items):
                        return
                    item_id = self.current_items[current_row].id
                    item = session.query(Animal).filter_by(id=item_id).first()
                    if not item:
                        return
                    session.delete(item)
                    session.commit()
                    self.show_animals()
                elif self.current_table == self.employees_table:
                    self.current_items = session.query(Employee).all()
                    if current_row >= len(self.current_items):
                        return
                    item_id = self.current_items[current_row].id
                    item = session.query(Employee).filter_by(id=item_id).first()
                    if not item:
                        return
                    session.delete(item)
                    session.commit()
                    self.show_employees()
                elif self.current_table == self.enclosures_table:
                    self.current_items = session.query(Enclosure).all()
                    if current_row >= len(self.current_items):
                        return
                    item_id = self.current_items[current_row].id
                    item = session.query(Enclosure).filter_by(id=item_id).first()
                    if not item:
                        return
                    session.delete(item)
                    session.commit()
                    self.show_enclosures()
                elif self.current_table == self.feeding_table:
                    self.current_items = session.query(AnimalFeed).all()
                    if current_row >= len(self.current_items):
                        return
                    item_id = self.current_items[current_row].id
                    item = session.query(AnimalFeed).filter_by(id=item_id).first()
                    if not item:
                        return
                    session.delete(item)
                    session.commit()
                    self.show_feeding()
                elif self.current_table == self.health_table:
                    self.current_items = session.query(HealthRecord).all()
                    if current_row >= len(self.current_items):
                        return
                    item_id = self.current_items[current_row].id
                    item = session.query(HealthRecord).filter_by(id=item_id).first()
                    if not item:
                        return
                    session.delete(item)
                    session.commit()
                    self.show_health()
                QMessageBox.information(self, "Успех", "Запись успешно удалена!")
            except Exception as e:
                session.rollback()
                QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении: {str(e)}")

    def search_items(self, text):
        if not text:
            if self.current_table == self.animals_table:
                self.show_animals()
            elif self.current_table == self.employees_table:
                self.show_employees()
            elif self.current_table == self.enclosures_table:
                self.show_enclosures()
            elif self.current_table == self.feeding_table:
                self.show_feeding()
            elif self.current_table == self.health_table:
                self.show_health()
            return
        with get_session() as session:
            text = text.lower()
            if self.current_table == self.animals_table:
                filtered_items = session.query(Animal).filter(
                    (Animal.name.ilike(f"%{text}%")) |
                    (Animal.fk_species.has(Species.name.ilike(f"%{text}%"))) |
                    (Animal.fk_enclosure.has(Enclosure.name.ilike(f"%{text}%")))
                ).all()
                headers = ["Имя", "Вид", "Вольер", "Дата рождения", "Дата прибытия", "Пол"]
                def get_animal_data(animal):
                    return [
                        animal.name,
                        animal.fk_species.name if animal.fk_species else "",
                        animal.fk_enclosure.name if animal.fk_enclosure else "",
                        animal.date_of_birth,
                        animal.date_of_arrival,
                        animal.sex
                    ]
                self.current_items = filtered_items
                self.animals_table.setRowCount(len(filtered_items))
                self.animals_table.setColumnCount(len(headers))
                self.animals_table.setHorizontalHeaderLabels(headers)
                for row, item in enumerate(filtered_items):
                    for col, value in enumerate(get_animal_data(item)):
                        self.animals_table.setItem(row, col, QTableWidgetItem(str(value)))
                self.animals_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

            elif self.current_table == self.employees_table:
                filtered_items = session.query(Employee).filter(
                    (Employee.name.ilike(f"%{text}%")) |
                    (Employee.position.ilike(f"%{text}%")) |
                    (Employee.phone.ilike(f"%{text}%"))
                ).all()
                headers = ["Имя", "Должность", "Телефон", "Дата найма"]
                def get_employee_data(employee):
                    return [employee.name, employee.position, employee.phone, employee.hire_date]
                self.current_items = filtered_items
                self.employees_table.setRowCount(len(filtered_items))
                self.employees_table.setColumnCount(len(headers))
                self.employees_table.setHorizontalHeaderLabels(headers)
                for row, item in enumerate(filtered_items):
                    for col, value in enumerate(get_employee_data(item)):
                        self.employees_table.setItem(row, col, QTableWidgetItem(str(value)))
                self.employees_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

            elif self.current_table == self.enclosures_table:
                filtered_items = session.query(Enclosure).filter(
                    (Enclosure.name.ilike(f"%{text}%")) |
                    (Enclosure.location.ilike(f"%{text}%")) |
                    (Enclosure.description.ilike(f"%{text}%"))
                ).all()
                headers = ["Название", "Размер (m²)", "Местоположение", "Описание"]
                def get_enclosure_data(enclosure):
                    return [enclosure.name, enclosure.size, enclosure.location, enclosure.description]
                self.current_items = filtered_items
                self.enclosures_table.setRowCount(len(filtered_items))
                self.enclosures_table.setColumnCount(len(headers))
                self.enclosures_table.setHorizontalHeaderLabels(headers)
                for row, item in enumerate(filtered_items):
                    for col, value in enumerate(get_enclosure_data(item)):
                        self.enclosures_table.setItem(row, col, QTableWidgetItem(str(value)))
                self.enclosures_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

            elif self.current_table == self.feeding_table:
                filtered_items = session.query(AnimalFeed).filter(
                    (AnimalFeed.fk_animal.has(Animal.name.ilike(f"%{text}%"))) |
                    (AnimalFeed.fk_feed.has(Feed.name.ilike(f"%{text}%")))
                ).all()
                headers = ["Животное", "Корм", "Суточная норма (кг)"]
                def get_feeding_data(animal_feed):
                    return [
                        animal_feed.fk_animal.name if animal_feed.fk_animal else "",
                        animal_feed.fk_feed.name if animal_feed.fk_feed else "",
                        animal_feed.daily_amount
                    ]
                self.current_items = filtered_items
                self.feeding_table.setRowCount(len(filtered_items))
                self.feeding_table.setColumnCount(len(headers))
                self.feeding_table.setHorizontalHeaderLabels(headers)
                for row, item in enumerate(filtered_items):
                    for col, value in enumerate(get_feeding_data(item)):
                        self.feeding_table.setItem(row, col, QTableWidgetItem(str(value)))
                self.feeding_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

            elif self.current_table == self.health_table:
                filtered_items = session.query(HealthRecord).filter(
                    (HealthRecord.fk_animal.has(Animal.name.ilike(f"%{text}%"))) |
                    (HealthRecord.notes.ilike(f"%{text}%"))
                ).all()
                headers = ["Животное", "Дата осмотра", "Заметки"]
                def get_health_data(health_record):
                    return [
                        health_record.fk_animal.name if health_record.fk_animal else "",
                        health_record.checkup_date,
                        health_record.notes
                    ]
                self.current_items = filtered_items
                self.health_table.setRowCount(len(filtered_items))
                self.health_table.setColumnCount(len(headers))
                self.health_table.setHorizontalHeaderLabels(headers)
                for row, item in enumerate(filtered_items):
                    for col, value in enumerate(get_health_data(item)):
                        self.health_table.setItem(row, col, QTableWidgetItem(str(value)))
                self.health_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

app = QApplication([])
window = MainWindow()
window.show()
app.exec()