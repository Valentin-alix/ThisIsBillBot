from src.gui.components.log_syntax_highlighter import LogSyntaxHighlighter
from src.gui.components.multi_selection_combobox import (
    MultiSelectComboBox,
    StayOpenMenu,
)
from src.gui.components.qfluent_widget.scrollable_message_box import (
    ScrollableMessageBox,
)
from src.gui.components.table.multi_filter_proxy import MultiColumnFilterProxyModel
from src.gui.components.table.table_view import CustomTableModel
from src.gui.fragments.sidebar_item import SidebarItem
from src.gui.fragments.sidebar_panel import SidebarPanel
from src.gui.pages.debugs.message_filter_proxy import MessageFilterProxyModel

_ = (
    LogSyntaxHighlighter.highlightBlock,
    StayOpenMenu._onItemClicked,
    MultiSelectComboBox,
    MultiSelectComboBox.selectedItemsData,
    MultiSelectComboBox._showComboMenu,
    MultiSelectComboBox._onItemClicked,
    MultiColumnFilterProxyModel.filterAcceptsRow,
    MessageFilterProxyModel.filterAcceptsRow,
    CustomTableModel.columnCount,
    CustomTableModel.flags,
    CustomTableModel.update_row_cells,
    SidebarItem.play_clicked,
    SidebarItem.stop_clicked,
    SidebarPanel.addSeparator,
    SidebarPanel.setExpandWidth,
    SidebarPanel.setMinimumExpandWidth,
    SidebarPanel.setAcrylicEnabled,
    ScrollableMessageBox,
)
