#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
统计对话框模块

提供小说统计功能，包括总字数、章节数、卷数等统计信息。
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QTabWidget, QWidget,
    QFormLayout, QProgressBar, QHeaderView
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np


class StatisticsDialog(QDialog):
    """统计对话框"""

    def __init__(self, parent, data_manager):
        """
        初始化统计对话框
        
        Args:
            parent: 父窗口
            data_manager: 数据管理器
        """
        super().__init__(parent)
        self.setWindowTitle("小说统计")
        self.resize(800, 600)
        self.data_manager = data_manager
        
        # 初始化UI
        self._init_ui()
        
        # 计算统计数据
        self._calculate_statistics()

    def _init_ui(self):
        """初始化UI"""
        # 创建主布局
        main_layout = QVBoxLayout(self)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # 创建概览标签页
        self.overview_tab = QWidget()
        overview_layout = QVBoxLayout(self.overview_tab)
        
        # 创建概览表单
        form_layout = QFormLayout()
        
        self.title_label = QLabel()
        form_layout.addRow("小说标题:", self.title_label)
        
        self.volume_count_label = QLabel()
        form_layout.addRow("卷数:", self.volume_count_label)
        
        self.chapter_count_label = QLabel()
        form_layout.addRow("章节数:", self.chapter_count_label)
        
        self.word_count_label = QLabel()
        form_layout.addRow("总字数:", self.word_count_label)
        
        self.avg_chapter_length_label = QLabel()
        form_layout.addRow("平均每章字数:", self.avg_chapter_length_label)
        
        self.completed_chapters_label = QLabel()
        form_layout.addRow("已完成章节:", self.completed_chapters_label)
        
        self.completion_rate_label = QLabel()
        form_layout.addRow("完成度:", self.completion_rate_label)
        
        overview_layout.addLayout(form_layout)
        
        # 创建进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        overview_layout.addWidget(self.progress_bar)
        
        # 创建图表
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        overview_layout.addWidget(self.canvas)
        
        self.tab_widget.addTab(self.overview_tab, "概览")
        
        # 创建卷统计标签页
        self.volume_tab = QWidget()
        volume_layout = QVBoxLayout(self.volume_tab)
        
        self.volume_table = QTableWidget()
        self.volume_table.setColumnCount(4)
        self.volume_table.setHorizontalHeaderLabels(["卷号", "卷标题", "章节数", "字数"])
        self.volume_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        volume_layout.addWidget(self.volume_table)
        
        self.tab_widget.addTab(self.volume_tab, "卷统计")
        
        # 创建章节统计标签页
        self.chapter_tab = QWidget()
        chapter_layout = QVBoxLayout(self.chapter_tab)
        
        self.chapter_table = QTableWidget()
        self.chapter_table.setColumnCount(5)
        self.chapter_table.setHorizontalHeaderLabels(["卷号", "章节号", "章节标题", "字数", "状态"])
        self.chapter_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        chapter_layout.addWidget(self.chapter_table)
        
        self.tab_widget.addTab(self.chapter_tab, "章节统计")
        
        # 创建按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.close_button = QPushButton("关闭")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)
        
        main_layout.addLayout(button_layout)

    def _calculate_statistics(self):
        """计算统计数据"""
        # 获取大纲
        outline = self.data_manager.get_outline()
        if not outline:
            return
        
        # 基本信息
        title = outline.get("title", "未命名小说")
        self.title_label.setText(title)
        
        volumes = outline.get("volumes", [])
        volume_count = len(volumes)
        self.volume_count_label.setText(str(volume_count))
        
        # 章节统计
        total_chapters = 0
        completed_chapters = 0
        total_words = 0
        volume_stats = []
        chapter_stats = []
        
        # 设置卷表格行数
        self.volume_table.setRowCount(volume_count)
        
        # 计算总章节数
        for i, volume in enumerate(volumes):
            volume_title = volume.get("title", f"第{i+1}卷")
            chapters = volume.get("chapters", [])
            chapter_count = len(chapters)
            total_chapters += chapter_count
            
            # 卷字数
            volume_words = 0
            volume_completed_chapters = 0
            
            # 章节统计
            for j, chapter in enumerate(chapters):
                chapter_title = chapter.get("title", f"第{j+1}章")
                
                # 获取章节内容
                content = self.data_manager.get_chapter(i, j)
                word_count = len(content) if content else 0
                
                # 更新统计
                volume_words += word_count
                total_words += word_count
                
                # 判断章节是否完成
                is_completed = word_count > 0
                if is_completed:
                    completed_chapters += 1
                    volume_completed_chapters += 1
                
                # 添加到章节统计
                chapter_stats.append({
                    "volume_index": i,
                    "chapter_index": j,
                    "title": chapter_title,
                    "word_count": word_count,
                    "is_completed": is_completed
                })
            
            # 添加到卷统计
            volume_stats.append({
                "volume_index": i,
                "title": volume_title,
                "chapter_count": chapter_count,
                "word_count": volume_words,
                "completed_chapters": volume_completed_chapters
            })
            
            # 更新卷表格
            self.volume_table.setItem(i, 0, QTableWidgetItem(str(i+1)))
            self.volume_table.setItem(i, 1, QTableWidgetItem(volume_title))
            self.volume_table.setItem(i, 2, QTableWidgetItem(str(chapter_count)))
            self.volume_table.setItem(i, 3, QTableWidgetItem(f"{volume_words:,}"))
        
        # 更新章节表格
        self.chapter_table.setRowCount(len(chapter_stats))
        for i, stat in enumerate(chapter_stats):
            self.chapter_table.setItem(i, 0, QTableWidgetItem(str(stat["volume_index"]+1)))
            self.chapter_table.setItem(i, 1, QTableWidgetItem(str(stat["chapter_index"]+1)))
            self.chapter_table.setItem(i, 2, QTableWidgetItem(stat["title"]))
            self.chapter_table.setItem(i, 3, QTableWidgetItem(f"{stat['word_count']:,}"))
            status = "已完成" if stat["is_completed"] else "未完成"
            status_item = QTableWidgetItem(status)
            status_item.setForeground(Qt.GlobalColor.darkGreen if stat["is_completed"] else Qt.GlobalColor.darkRed)
            self.chapter_table.setItem(i, 4, status_item)
        
        # 更新概览信息
        self.chapter_count_label.setText(str(total_chapters))
        self.word_count_label.setText(f"{total_words:,}")
        
        avg_chapter_length = total_words / total_chapters if total_chapters > 0 else 0
        self.avg_chapter_length_label.setText(f"{avg_chapter_length:.2f}")
        
        self.completed_chapters_label.setText(f"{completed_chapters} / {total_chapters}")
        
        completion_rate = (completed_chapters / total_chapters * 100) if total_chapters > 0 else 0
        self.completion_rate_label.setText(f"{completion_rate:.2f}%")
        
        # 更新进度条
        self.progress_bar.setValue(int(completion_rate))
        
        # 绘制图表
        self._draw_charts(volume_stats, chapter_stats)

    def _draw_charts(self, volume_stats, chapter_stats):
        """绘制图表"""
        self.figure.clear()
        
        # 创建子图
        ax1 = self.figure.add_subplot(121)
        ax2 = self.figure.add_subplot(122)
        
        # 卷字数统计图
        volume_indices = [stat["volume_index"]+1 for stat in volume_stats]
        volume_words = [stat["word_count"] for stat in volume_stats]
        
        ax1.bar(volume_indices, volume_words)
        ax1.set_title("各卷字数统计")
        ax1.set_xlabel("卷号")
        ax1.set_ylabel("字数")
        ax1.set_xticks(volume_indices)
        
        # 章节字数分布图
        chapter_words = [stat["word_count"] for stat in chapter_stats if stat["word_count"] > 0]
        if chapter_words:
            ax2.hist(chapter_words, bins=10)
            ax2.set_title("章节字数分布")
            ax2.set_xlabel("字数")
            ax2.set_ylabel("章节数")
        
        self.figure.tight_layout()
        self.canvas.draw()
