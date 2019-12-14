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
import chat

class SummonerSpell(enum.IntEnum):
	BARRIER = 180
	CLEANSE = 210
	EXHAUST = 210
	FLASH = 300
	GHOST = 180
	HEAL = 240
	IGNITE = 180
	SMITE = 60
	TELEPORT = 360
			
class SummonerSpellThread(QThread,QObject):
	
	print_thread = QtCore.Signal(str)
	update_progressbar = QtCore.Signal(int)
		
	def __init__(self,parent=None,summoner_spell=None):
		QThread.__init__(self,parent)
		
		self.mutex = QtCore.QMutex()
		self.stopped = False
		self.summoner_spell = summoner_spell
		self.sum_label = QObject
		self.second = summoner_spell
		
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

		progress_value = 0
		while not self.stopped:
			self.second -= 1
			progress_value += 1
			self.print_thread.emit(str(self.second))
			self.update_progressbar.emit(progress_value)
			time.sleep(1)

			if self.second <= 0:
				self.stopped = True	
				
class SpellWindow(QWidget):
	def __init__(self,parent=None):
		super(SpellWindow,self).__init__(parent)
		self.w = QUiLoader().load("spell_window.ui")
		#最前面に表示されるように。
		self.w.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
		
		spell_button_list = [self.w.toolButton_1,self.w.toolButton_2,self.w.toolButton_3,self.w.toolButton_4,self.w.toolButton_5,self.w.toolButton_6,self.w.toolButton_7,self.w.toolButton_8,self.w.toolButton_9]
		#なぜかint型にしないと正常にzipされない	1214なぜかint型じゃなくても正常にじpされる				
		taiou_list = [SummonerSpell.BARRIER,SummonerSpell.CLEANSE,SummonerSpell.EXHAUST,SummonerSpell.FLASH,SummonerSpell.GHOST,SummonerSpell.HEAL,SummonerSpell.IGNITE,SummonerSpell.SMITE,SummonerSpell.TELEPORT]
		
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
		
		self.ui = QUiLoader().load("league_timer.ui")
		self.setCentralWidget(self.ui)
		
		self.a = [None] * 10
		
		###各種オブジェクトをグループ化する処理
		self.button_name_list = [self.ui.top_sum1_button,self.ui.top_sum2_button,self.ui.jg_sum1_button,self.ui.jg_sum2_button,self.ui.mid_sum1_button,self.ui.mid_sum2_button,
							self.ui.bot_sum1_button,self.ui.bot_sum2_button,self.ui.sup_sum1_button,self.ui.sup_sum2_button]
							
		self.label_name_list = [self.ui.top_sum1_cd,self.ui.top_sum2_cd,self.ui.jg_sum1_cd,self.ui.jg_sum2_cd,self.ui.mid_sum1_cd,self.ui.mid_sum2_cd,
							self.ui.bot_sum1_cd,self.ui.bot_sum2_cd,self.ui.sup_sum1_cd,self.ui.sup_sum2_cd]
							
		self.progressbar_list = [self.ui.top_sum1_bar,self.ui.top_sum2_bar,self.ui.jg_sum1_bar,self.ui.jg_sum2_bar,self.ui.mid_sum1_bar,self.ui.mid_sum2_bar,
							self.ui.bot_sum1_bar,self.ui.bot_sum2_bar,self.ui.sup_sum1_bar,self.ui.sup_sum2_bar]
							
		self.spell_list = [SummonerSpell.TELEPORT,SummonerSpell.FLASH,SummonerSpell.SMITE,SummonerSpell.FLASH,SummonerSpell.IGNITE,SummonerSpell.FLASH,SummonerSpell.HEAL,SummonerSpell.FLASH,SummonerSpell.EXHAUST,SummonerSpell.FLASH]
		
		self.zipped_list = [list(i) for i in zip(self.button_name_list,self.label_name_list,self.progressbar_list,self.spell_list)]	
		###
		
		#デフォルトのサモナースペル
		self.summoner_spell_button_list = [self.ui.summonerspell01,self.ui.summonerspell02,self.ui.summonerspell03,self.ui.summonerspell04,self.ui.summonerspell05,self.ui.summonerspell06,self.ui.summonerspell07,self.ui.summonerspell08,self.ui.summonerspell09,self.ui.summonerspell10]

		###サモナースペルを適応する
		for index,spell_button in enumerate(self.summoner_spell_button_list):
			spell_button.clicked.connect(functools.partial(self.change_summonerspell,index=index,button=spell_button))
		self.setting_spell_button()
		###
		
		self.ui.chat_button.clicked.connect(self.aaaa)
					
		self.resize(400,770)
	
	'''
	全てのボタンにサモナースペルを適応する。
	'''
	def setting_spell_button(self):
		for index,(button,label,progress,summoner_spell) in enumerate(self.zipped_list):
			try: button.clicked.disconnect()
			except RuntimeError: pass
			
			button.clicked.connect(functools.partial(
													self.count_summonerspell, 
													sum_label=label,
													progressbar = progress,
													spell =summoner_spell,
													index = index)
													)
	
	'''
	spellwindowを開く
	'''
	def change_summonerspell(self,index,button):
		#ここで自分のqwidgeを送る。送った先で画像を変更する。
		spell.open(index,button)
				
	'''
	タイマースレッドの処理
	'''
	def count_summonerspell(self,sum_label,progressbar,spell,index):
		thread = SummonerSpellThread(sum_label,spell)
		if not self.a[index] == None:
			self.a[index].stop()
			del(self.a[index])
		self.a[index] = thread

		thread.print_thread.connect(functools.partial(self.update_text,label=sum_label))
		progressbar.setMaximum(spell)
		thread.update_progressbar.connect(functools.partial(self.update_progressbar,progress=progressbar))
		thread.start()

	'''
	スレッドと通信してる
	'''	
	def update_progressbar(self,value,progress):
		progress.setValue(value)
		
	'''
	スレッドと通信してる
	'''	
	def update_text(self,second_data,label):
		minute,second = divmod(int(second_data), 60)
		label.setText('{:02d}:{:02d}'.format(minute, second))
	
	'''
	実行中のスレッドを取得
	それのタイマーを取得
	'''	
	def aaaa(self):
		self.check_thread()
		text = ""
		role = ["top","jg","mid","ad","sup"]
		
		for index,aa in enumerate(self.a,1):
			if index % 2 == 0:
				role.pop(0)

			if not aa == None:
				if not index % 2 == 0:
					text += role[0] + " "
					
				text += str(aa.summoner_spell)
				text += str(aa.second) + "s" + " "
		
		text = text.replace("SummonerSpell.","")
		text = text.lower()
		text = text.replace("teleport","tp")
		chat.chat(text)
	
	def check_thread(self):
		for index,a in enumerate(self.a):
			if not a is None and not a.isRunning():
					del(self.a[index])	
					
if __name__ == "__main__":
	
	QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
	app = QApplication(sys.argv)
	timer = LeagueTimer()
	spell = SpellWindow()
	timer.show()
	sys.exit(app.exec_())