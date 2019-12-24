import sys
from PySide2 import QtXml
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import *
from PySide2 import QtWidgets
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2 import QtCore
import enum
import time
import functools
import chat

class SummonerSpell(enum.IntEnum):
	BARRIER = 181
	CLEANSE = 211
	EXHAUST = 210
	FLASH = 300
	GHOST = 179
	HEAL = 240
	IGNITE = 180
	SMITE = 60
	TELEPORT = 360
			
class SummonerSpellThread(QThread,QObject):
	
	print_thread = QtCore.Signal(str)
	update_progressbar = QtCore.Signal(int)
		
	def __init__(self, parent=None, summoner_spell=None):
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
			self.isRunning = False

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
				self.update_progressbar.emit(0)
				self.stop()

				
				
class SpellWindow(QWidget):
	def __init__(self,parent=None):
		super(SpellWindow, self).__init__(parent)
		self.w = QUiLoader().load("spell_window.ui")
		#self.w = Ui_Form()
		#self.w.setupUi(self)
		self.w.setWindowFlags(Qt.WindowStaysOnTopHint)

		spell_button_list = [self.w.toolButton_1,self.w.toolButton_2,self.w.toolButton_3,self.w.toolButton_4,self.w.toolButton_5,self.w.toolButton_6,self.w.toolButton_7,self.w.toolButton_8,self.w.toolButton_9]
		taiou_list = [SummonerSpell.BARRIER,SummonerSpell.CLEANSE,SummonerSpell.EXHAUST,SummonerSpell.FLASH,SummonerSpell.GHOST,SummonerSpell.HEAL,SummonerSpell.IGNITE,SummonerSpell.SMITE,SummonerSpell.TELEPORT]
		#をenumerate(zip(a, b)し、connectfunctool。クリックされたらsetting_buttonで。leaguetimerのspelllistを書き換える。
		for button,spell in zip(spell_button_list,taiou_list):
			button.clicked.connect(functools.partial(self.update_spell_button,selected_spell=spell,spell_button=button))
		
	def open(self,index,button):
		self.w.show()
		self.index = index
		self.last_button = button
		
	def update_spell_button(self,selected_spell,spell_button):
		#.icon x
		self.last_button.setIcon(spell_button.icon())
		main.zipped_list[self.index][3] = selected_spell

		main.setting_spell_button()
		self.w.close()		
	
class LeagueTimer(QMainWindow):
		
	def __init__(self,parent=None):
		super(LeagueTimer,self).__init__()		
		self.ui = QUiLoader().load("league_timer.ui")
		self.setCentralWidget(self.ui)
		
		self.thread_list = [None] * 10
		
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
		for index,button in enumerate(self.summoner_spell_button_list):
			button.clicked.connect(functools.partial(self.change_summonerspell,index=index,button=button))	
		self.setting_spell_button()
		###
		
		self.ui.chat_button.clicked.connect(self.generate_chat_text)
		self.resize(400,770)
	
	def setting_spell_button(self):
		'''ボタン設定を反映する。
		'''
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
	
	def change_summonerspell(self,index,button):
		'''SpellWindowを開く
		'''
		#ここで自分のqwidgeを送る。送った先で画像を変更する。
		spell.open(index,button)
				
	def count_summonerspell(self,sum_label,progressbar,spell,index):
		'''タイマースレッドのインスタンスを生成する。
		'''
		thread = SummonerSpellThread(sum_label,spell)
		#生きてるスレッドを上書きする処理
		if not self.thread_list[index] == None:
			self.thread_list[index].stop()
			self.thread_list[index] = None
		self.thread_list[index] = thread

		thread.print_thread.connect(functools.partial(self.update_text,label=sum_label))
		progressbar.setMaximum(spell)
		thread.update_progressbar.connect(functools.partial(self.update_progressbar,progress=progressbar))
		thread.start()

	def update_progressbar(self,value,progress):
		'''スレッドと通信してる
		'''	
		progress.setValue(value)
		

	def update_text(self,second_data,label):
		'''スレッドと通信してる
		'''	
		minute,second = divmod(int(second_data), 60)
		label.setText('{:02d}:{:02d}'.format(minute, second))
	

	def generate_chat_text(self):
		'''チャットに使うテキストを生成する。
		'''	
		self.check_thread()
		text = ""
		role = ["top","jg","mid","ad","sup"]
		have_added_role = False

		for index,thread in enumerate(self.thread_list):
			#スレッドが生きていて
			if thread is not None:
				if index in [0,2,4,6,8]:
					text += role[0] + " "
					have_added_role = True

				elif not have_added_role:
					text += role[0] + " "
			
				text += str(thread.summoner_spell)
				text += str(thread.second) + "s" + " "

			if index in[1,3,5,7]:
				have_added_role = False
				role.pop(0)
		
		text = text.replace("SummonerSpell.","")
		text = text.lower()
		text = text.replace("teleport","tp")
		text = text.replace("flash","f")

		chat.chat(text)
	
	def check_thread(self):
		'''スレッドが生きているかを確認する。
		'''
		for index,a in enumerate(self.thread_list):
			if not a is None and not a.isRunning():
					self.thread_list[index] = None
					
if __name__ == "__main__":
	
	QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
	app = QApplication(sys.argv)
	main = LeagueTimer()
	spell = SpellWindow()
	main.show()
	sys.exit(app.exec_())