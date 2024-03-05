# Checkpoint Tool
此标注工具是一个web端工具，它用来对于已经获取到的任务的标准执行流程来标注相应的checkpoint，主要基于Flask框架来实现。标注的内容会在原路径下保存.text的标注文件。
## Get Started

1. Clone the repository to your local machine:

   ```sh
   git clone 
   ```

2. Navigate to the cloned repository:

   ```sh
   cd Checkpoint_Tool/
   ```

3. Install the required dependencies:

   ```sh
   pip install -r requirements.txt
   ```

4. python app.py

## 标注工具的使用逻辑

### 提交路径，选中trace并标注
1、在路径中给出general,install或者webshopping的文件夹路径，即trace的上一级文件夹，然后点击submit
2、左侧边栏显示trace名称（目前是乱序）可配合浏览器搜索功能确定具体trace位置，点击左边栏的trace_*，右侧上端会显示出picture和文本框
3、标注完成过后，点击annonate提交标注

### 模糊匹配
1、选中的图片默认进行全局的模糊匹配，等同于fuzzy_match<-1>;
2、如果要区域进行模糊匹配，可以在<>中指明明确的node-id比如fuzzy_match<0>代表的意思是在node-0的周围进行模糊匹配，忽略其他区域; 
3、fuzzy_match<-2>意味着虽然选中此界面，但并不需要模糊匹配，直接匹配其他关键字；

### 精确匹配
支持的关键字有：
click<node-id>: 确认是否点击了某个node
textbox<node-id> 确认某个文字是否存在
activity<-1> 确认当前界面的activity
check_install<app_name> 确认是否安装了某个app
check_uninstall<app_name> 确认是否卸载了某个app
button<1:state> 确认某个button的状态。state = on or off

### 关键字组合
关键字之间用|来分割
example: fuzzy_match<0>|textbox<0>|activity<-1>
