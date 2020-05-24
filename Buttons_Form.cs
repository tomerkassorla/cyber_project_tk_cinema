using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace WindowsFormsApplication8
{
    public partial class Buttons_Form : Form
    {
        private string directory = "";
        private Boolean close = true;
        private Boolean open = true;
        public Buttons_Form()
        {
            InitializeComponent();
            project_path path = new project_path();
            this.directory = path.get_project_path();
            this.label1.Text = "use this buttons to control the video";
            this.button5.Image = Image.FromFile(directory + "mute.png");
            this.button2.Image = Image.FromFile(directory + "pause.jpg");
            this.button3.Image = Image.FromFile(directory + "plus.png");
        }

        private void ButtonsForm_FormClosing(object sender, FormClosingEventArgs e)
        {
            SingleConnection.send("close");
            Console.WriteLine("here after hide");
            //SingleConnection.StopPythonEngine();
            while (this.open && this.close)
            {
                Console.WriteLine("wait");
            }
            this.Hide();
            if (this.open)
            {
                Select_Video_Form f1 = new Select_Video_Form();
                f1.ShowDialog();
            }
        }

        private void button1_Click(object sender, EventArgs e)
        {
        }
        private void ButtonsForm_Load(object sender, EventArgs e)
        {
            Thread thr = new Thread(new ThreadStart(this.receive_thread));
            thr.Start(); 
        }
        private void receive_thread()
        {
            string message = SingleConnection.recv();
            Console.WriteLine(message);
            if (message.Equals("finish and open rate"))
            {
                if (InvokeRequired)
                {
                    this.open = false;
                    this.Invoke(new Action(() => { FormHandler1(); }));
                }
            }
            if (message.Equals("closing the thread in buttonsForm and open"))
            {
                this.close = false;
            }
            else
            {
                this.open = false;
            }
        }
        private void FormHandler1()
        {
            SingleConnection.send("close the wait for commands thread in client");
            Console.WriteLine("hide");
            this.Hide();
            Rate_Form f2 = new Rate_Form();
            f2.ShowDialog();
        }
        private void button3_Click(object sender, EventArgs e)
        {
            SingleConnection.send("plus");
        }

        private void button4_Click(object sender, EventArgs e)
        {
        }

        private void button2_Click(object sender, EventArgs e)
        {
            SingleConnection.send("stop");
        }

        private void button5_Click(object sender, EventArgs e)
        {
            SingleConnection.send("mute");
        }

        private void label1_Click(object sender, EventArgs e)
        {

        }
    }
}
