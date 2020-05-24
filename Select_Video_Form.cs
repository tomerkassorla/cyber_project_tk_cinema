using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace WindowsFormsApplication8
{
    public partial class Select_Video_Form : Form
    {
        private string pic_directory = "";
        private Dictionary<string, int> movie_time_dict;
        private Dictionary<string, float> movie_rate_dict;
        private string [] download_videos_array;
        private int time;
        private Boolean with_for = true;
        public Select_Video_Form()
        {
            InitializeComponent();
            project_path path = new project_path();
            this.pic_directory = path.get_project_path();
            //this.listView1.BackgroundImage = Image.FromFile(pic_directory+ "\\" + "videos_background.jpg");
            this.listView1.BackColor = Color.DimGray;
            this.BackColor = Color.Black;
            this.textBox1.AutoSize = false;
            this.textBox1.Size = new System.Drawing.Size(337, 30);
            string[] files = Directory.GetFiles(pic_directory, "*.bmp", SearchOption.AllDirectories);
            imageList1.ImageSize = new Size(128, 128);
            for (int i = 0; i < files.Length; i++)
            {
                string fileName = Path.GetFileName(files[i]);
                fileName = fileName.Remove(fileName.Length - 4);
                imageList1.Images.Add(Image.FromFile(files[i]));
                listView1.Items.Add(fileName);
                listView1.Items[i].ImageIndex = i;
            }
            listView1.LargeImageList = imageList1;
            
        }

        private void button1_Click(object sender, EventArgs e)
        {

        }

        private void button1_MouseEnter(object sender, EventArgs e)
        {

        }
        private Dictionary<string, int> convert_movie_time_str_to_dict(string movie_time_str)
        {
            Dictionary<string, int> result = new Dictionary<string, int>();
            if (movie_time_str.Equals(""))
                return result;
            string[] array_movie_time = movie_time_str.Split(';');
            Array.Resize(ref array_movie_time, array_movie_time.Length-1);
            for (int i = 0; i < array_movie_time.Length; i++)
            {
                String movie_name = array_movie_time[i].Split('@')[0];
                int movie_time = Int32.Parse(array_movie_time[i].Split('@')[1]);
                result.Add(movie_name, movie_time);
            }
            return result;
           
        }
        private Dictionary<string, float> convert_movies_rates_str_to_dict(string movies_rates)
        {
            Dictionary<string, float> result = new Dictionary<string, float>();
            if (movies_rates.Equals(""))
                return result;
            string[] array_movie_rate = movies_rates.Split('*');
            Array.Resize(ref array_movie_rate, array_movie_rate.Length - 1);
            for (int i = 0; i < array_movie_rate.Length; i++)
            {
                String movie_name = array_movie_rate[i].Split('%')[0];
                float movie_rate = float.Parse(array_movie_rate[i].Split('%')[1]);
                result.Add(movie_name, movie_rate);
            }
            return result;
        }
        private void Form1_Load(object sender, EventArgs e)
        {
            Thread thr = new Thread(new ThreadStart(this.receive_thread));
            thr.Start(); 
        }
        private void receive_thread()
        {
            if (InvokeRequired)
            {
                Console.WriteLine("here");
                this.Invoke(new Action(() => { FormHandler(); }));
            }
        }
        private Boolean video_is_download(string name)
        {
            for (int i = 0; i < this.download_videos_array.Length; i++)
            {
                if (this.download_videos_array[i].Equals(name))
                    return true;
            }
            return false;
        }
        private void FormHandler()
        {
            string s = SingleConnection.recv();
            Console.WriteLine(s);
            string[] movie_time_rate_download = s.Split('$');
            string movie_time_str = movie_time_rate_download[0];
            string movies_rates = movie_time_rate_download[1];
            string download_videos = movie_time_rate_download[2];
            this.movie_time_dict = convert_movie_time_str_to_dict(movie_time_str);
            this.movie_rate_dict = convert_movies_rates_str_to_dict(movies_rates);
            this.download_videos_array = download_videos.Split('&');
            Array.Resize(ref this.download_videos_array, this.download_videos_array.Length - 1);
        }
        private void listView1_ItemSelectionChanged(object sender, ListViewItemSelectionChangedEventArgs e)
        {

        }
        void SaveData()
        {
            if (this.with_for)
            {
                for (int i = 0; i <= this.time * 60 ; i++)
                    Thread.Sleep(10);
                Console.WriteLine(this.time * 75);
            }
            else
            {
                while (!this.with_for)
                {
                    Thread.Sleep(10);
                }
            }
        }
        void menuItem_Click(object sender, EventArgs e)
        {
            ToolStripItem menuItem = (ToolStripItem)sender;
            string name = listView1.SelectedItems[0].Text;
            if (menuItem.Name == "play")
            {
                
                SingleConnection.send(name); // send the name of the song that pressed
                this.Hide();
                Buttons_Form bf = new Buttons_Form();
                bf.ShowDialog();
            }
            if (menuItem.Name == "Play from the last viewing point")
            {
                SingleConnection.send(name + "#" + this.movie_time_dict[name]);
                this.Hide();
                this.time = (this.movie_time_dict[name] / 3) +1;
                Console.WriteLine(this.time);
                this.with_for = true;
                using (Loading_Form f_load = new Loading_Form(SaveData))
                {
                    f_load.ShowDialog(this);
                }
                Buttons_Form bf = new Buttons_Form();
                bf.ShowDialog();
            }
            if (menuItem.Name == "Download for later viewing")
            {
                this.Hide();
                SingleConnection.send("Download@"+name);
                this.with_for = false;
                Thread download_thread = new Thread(new ThreadStart(this.download));
                download_thread.Start(); 
                using (Loading_Form f_load = new Loading_Form(SaveData))
                {
                    f_load.ShowDialog(this);
                }
                Select_Video_Form f1 = new Select_Video_Form();
                f1.ShowDialog();
            }
            if (menuItem.Name == "Play without connection")
            {
                SingleConnection.send("play_without_connection!" + name);
                this.Hide();
                Buttons_Form bf = new Buttons_Form();
                bf.ShowDialog();
               
            }
        } 
        private void download()
        {
            string str = SingleConnection.recv();
            Console.WriteLine(str);
            this.with_for = true;
        }
        private void listView1_ItemActivate(object sender, EventArgs e)
        {
        }

     

        private void listView1_SelectedIndexChanged(object sender, EventArgs e)
        {
            if (listView1.SelectedItems.Count == 0)
            {
                this.ContextMenuStrip = null;
            }

        }

        private void listView1_MouseClick(object sender, MouseEventArgs e)
        {
            string name = listView1.SelectedItems[0].Text;
            if (e.Button == MouseButtons.Right)
            {

                ContextMenuStrip menuStrip = new ContextMenuStrip();
                ToolStripMenuItem menuItem1 = new ToolStripMenuItem("Play");
                menuStrip.Items.Add(menuItem1);
                menuItem1.Click += new EventHandler(menuItem_Click);
                menuItem1.Name = "play";
                if (video_is_download(name))
                {
                    ToolStripMenuItem menuItem4 = new ToolStripMenuItem("Play without connection");
                    menuStrip.Items.Add(menuItem4);
                    menuItem4.Click += new EventHandler(menuItem_Click);
                    menuItem4.Name = "Play without connection";
                }
                else
                {
                    ToolStripMenuItem menuItem4 = new ToolStripMenuItem("Download for later viewing");
                    menuStrip.Items.Add(menuItem4);
                    menuItem4.Click += new EventHandler(menuItem_Click);
                    menuItem4.Name = "Download for later viewing";
                }
                if (this.movie_time_dict.ContainsKey(name))
                {
                    ToolStripMenuItem menuItem2 = new ToolStripMenuItem("Play from the last viewing point- " + this.movie_time_dict[name] + " sec");
                    menuStrip.Items.Add(menuItem2);
                    menuItem2.Click += new EventHandler(menuItem_Click);
                    menuItem2.Name = "Play from the last viewing point";
                }
                if (this.movie_rate_dict.ContainsKey(name))
                {
                    ToolStripMenuItem menuItem3 = new ToolStripMenuItem("Rate: " + this.movie_rate_dict[name]);
                    menuStrip.Items.Add(menuItem3);
                }
                this.ContextMenuStrip = menuStrip;
            }
            else
            {
                SingleConnection.send(name); // send the name of the song that pressed
                this.Hide();
                Buttons_Form bf = new Buttons_Form();
                bf.Show();
            }
        }

        private void listView1_ItemMouseHover(object sender, ListViewItemMouseHoverEventArgs e)
        {
          
        }

        private void listView1_MouseLeave(object sender, EventArgs e)
        {
            
        }

        private void listView1_ItemCheck(object sender, ItemCheckEventArgs e)
        {
        }
        private void change_list_view(string message)
        {
            if (!message.Equals("##"))
            {
                string[] array_of_names = message.Split('#');
                Array.Resize(ref array_of_names, array_of_names.Length - 1);
                string[] files = new string[array_of_names.Length];
                //listView1.Visible = false;
                imageList1.Images.Clear();
                listView1.Items.Clear();
                for (int i = 0; i < array_of_names.Length; i++)
                {
                    files[i] = this.pic_directory +"\\"+ array_of_names[i] + ".bmp";
                    imageList1.Images.Add(Image.FromFile(files[i]));
                    listView1.Items.Add(array_of_names[i]);
                    listView1.Items[i].ImageIndex = i;
                }
                listView1.LargeImageList = imageList1;
            }
        }
        private void textBox1_TextChanged(object sender, EventArgs e)
        {
            SingleConnection.send("%"+textBox1.Text);
            string message = SingleConnection.recv();
            this.change_list_view(message);
        }

        private void textBox1_MouseDown(object sender, MouseEventArgs e)
        {
            textBox1.Text = "";
        }
    }
}
