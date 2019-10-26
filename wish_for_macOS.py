import sys
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2 import QtCore
import enum
import time
import functools
import datetime


class SummonerSpell(enum.IntEnum):
	BARRIER = 180
	CLEANSE = 210
	EXHAUST = 210
	FLASH = 300
	GHOST = 180
	HEAL = 240
	IGNITE = 180
	SMITE = 15
	TELEPORT = 360
"""
class TimerThread(QThread):
	
	print_thread = QtCore.Signal(str)
	
	def __init__(self,parent=None):
		QThread.__init__(self,parent)
		
		self.mutex = QtCore.QMutex()
		self.stopped = False
		
	def __del__(self):
		self.stop()
		self.wait()
		
	def stop(self):
		with QtCore.QMutexLocker(self.mutex):
			self.stopped = True

	def restart(self):

		with QtCore.QMutexLocker(self.mutex):
			self.stopped = False

	def run(self):

		second = 0
		while not self.stopped:
			self.print_thread.emit(str(second))
			print(second)
			second += 1
			time.sleep(1)
"""
			
class SummonerSpellThread(QThread,QObject):
	
	#print_thread = QtCore.Signal([str,'QObject'])
	print_thread = QtCore.Signal(str)
	update_progressbar = QtCore.Signal(int)
		
	def __init__(self,parent=None,summoner_spell=None):
		QThread.__init__(self,parent)
		
		self.mutex = QtCore.QMutex()
		self.stopped = False
		self.summoner_spell = summoner_spell
		self.sum_label = QObject
		
	def __del__(self):
		self.stop()
		self.wait()
		
	def stop(self):
		with QtCore.QMutexLocker(self.mutex):
			self.stopped = True

	def restart(self):

		with QtCore.QMutexLocker(self.mutex):
			self.stopped = False

	def run(self):

		second = self.summoner_spell
		progress_value = 0
		while not self.stopped:
			second -= 1
			progress_value += 1
			self.print_thread.emit(str(second))
			self.update_progressbar.emit(progress_value)
			time.sleep(1)

			if second <= 0:
				self.stopped = True	
				
class SpellWindow(QWidget):
	def __init__(self,parent=None):
		super(SpellWindow,self).__init__(parent)
		self.w = QUiLoader().load("spell_window.ui")
		#最前面に表示されるように。
		self.w.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
		
		spell_button_list = [self.w.toolButton_1,self.w.toolButton_2,self.w.toolButton_3,self.w.toolButton_4,self.w.toolButton_5,self.w.toolButton_6,self.w.toolButton_7,self.w.toolButton_8,self.w.toolButton_9]
		#なぜかint型にしないと正常にzipされない					
		taiou_list = [int(SummonerSpell.BARRIER),int(SummonerSpell.CLEANSE),int(SummonerSpell.EXHAUST),int(SummonerSpell.FLASH),int(SummonerSpell.GHOST),int(SummonerSpell.HEAL),int(SummonerSpell.IGNITE),int(SummonerSpell.SMITE),int(SummonerSpell.TELEPORT)]
		
		#これらをenumerate(zip(a, b)し、connectfunctool。クリックされたらsetting_buttonで。leaguetimerのspelllistを書き換える。
		for button,spell in zip(spell_button_list,taiou_list):
			button.clicked.connect(functools.partial(self.update_spell_button,selected_spell=spell,spell_button=button))
		
		
	def open(self,index,button):
		self.w.show()
		self.index = index
		self.last_button = button
		
	def update_spell_button(self,selected_spell,spell_button):
		#.icon x
		self.last_button.setIcon(spell_button.icon())
		timer.zipped_list[self.index][3] = selected_spell

		timer.setting_spell_button()
		self.w.close()		
	
class LeagueTimer(QMainWindow):
		
	def __init__(self,parent=None):
		super(LeagueTimer,self).__init__(parent)		
		
		# ui ファイルを開く
		self.ui = QUiLoader().load("league_timer.ui")
		self.setCentralWidget(self.ui)

		#self.thread = TimerThread()
		#self.thread.print_thread.connect(functools.partial(self.log,label=self.ui.livegame_time))
		
		#signal
		#self.ui.start_game_button.clicked.connect(lambda:self.thread.start())
		
		self.button_name_list = [self.ui.top_sum1_button,self.ui.top_sum2_button,self.ui.jg_sum1_button,self.ui.jg_sum2_button,self.ui.mid_sum1_button,self.ui.mid_sum2_button,
							self.ui.bot_sum1_button,self.ui.bot_sum2_button,self.ui.sup_sum1_button,self.ui.sup_sum2_button]
							
		self.label_name_list = [self.ui.top_sum1_cd,self.ui.top_sum2_cd,self.ui.jg_sum1_cd,self.ui.jg_sum2_cd,self.ui.mid_sum1_cd,self.ui.mid_sum2_cd,
							self.ui.bot_sum1_cd,self.ui.bot_sum2_cd,self.ui.sup_sum1_cd,self.ui.sup_sum2_cd]
							
		self.progressbar_list = [self.ui.top_sum1_bar,self.ui.top_sum2_bar,self.ui.jg_sum1_bar,self.ui.jg_sum2_bar,self.ui.mid_sum1_bar,self.ui.mid_sum2_bar,
							self.ui.bot_sum1_bar,self.ui.bot_sum2_bar,self.ui.sup_sum1_bar,self.ui.sup_sum2_bar]
							
		self.spell_list = [SummonerSpell.TELEPORT,SummonerSpell.FLASH,SummonerSpell.SMITE,SummonerSpell.FLASH,SummonerSpell.IGNITE,SummonerSpell.FLASH,SummonerSpell.HEAL,SummonerSpell.FLASH,SummonerSpell.EXHAUST,SummonerSpell.FLASH]
		
		self.zipped_list = [list(i) for i in zip(self.button_name_list,self.label_name_list,self.progressbar_list,self.spell_list)]	
		
		self.summoner_spell_button_list = [self.ui.summonerspell01,self.ui.summonerspell02,self.ui.summonerspell03,self.ui.summonerspell04,self.ui.summonerspell05,self.ui.summonerspell06,self.ui.summonerspell07,self.ui.summonerspell08,self.ui.summonerspell09,self.ui.summonerspell10]
		
		for index,spell_button in enumerate(self.summoner_spell_button_list):
			spell_button.clicked.connect(functools.partial(self.change_summonerspell,index=index,button=spell_button))
					
		self.setting_spell_button()
		self.resize(400,770)
		
	def setting_spell_button(self):
		for button,label,progress,summoner_spell in self.zipped_list:
			try: button.clicked.disconnect()
			except RuntimeError: pass
			button.clicked.connect(functools.partial(self.count_summonerspell, sum_label=label,progressbar = progress,selected_spell =summoner_spell))
		
	def change_summonerspell(self,index,button):
		#ここで自分のqwidgeを送る。送った先で画像を変更する。
		spell.open(index,button)
		print(button)
				
	#二度ボタンを押したら前のスレッド削除して
	def count_summonerspell(self,sum_label,progressbar,selected_spell):
		thread = SummonerSpellThread(sum_label,selected_spell)
		thread.print_thread.connect(functools.partial(self.log,label=sum_label))
		progressbar.setMaximum(selected_spell)
		thread.update_progressbar.connect(functools.partial(self.update_progressbar,progress=progressbar))
		thread.start()

		
	def update_progressbar(self,value,progress):
		progress.setValue(value)
	
	def log(self,second_data,label):
		minute,second = divmod(int(second_data), 60)
		label.setText('{:02d}:{:02d}'.format(minute, second))			

	
if __name__ == "__main__":
	
	QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
	app = QApplication(sys.argv)
	timer = LeagueTimer()
	spell = SpellWindow()
	#spell.setParent(timer)
	timer.show()
	sys.exit(app.exec_())