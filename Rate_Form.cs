using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace WindowsFormsApplication8
{
    public partial class Rate_Form : Form
    {
        private string directory = "";
        private int counter = 0;
        public Rate_Form()
        {
            InitializeComponent();
            project_path path = new project_path();
            this.directory = path.get_project_path();
            this.button1.Image = Image.FromFile(directory + "white_star.png");
            this.button2.Image = Image.FromFile(directory + "white_star.png");
            this.button3.Image = Image.FromFile(directory + "white_star.png");
            this.button4.Image = Image.FromFile(directory + "white_star.png");
            this.button5.Image = Image.FromFile(directory + "white_star.png");
        }

        private void Form2_Load(object sender, EventArgs e)
        {
        }

        private void button1_Click(object sender, EventArgs e)
        {
            counter = 1;
            this.button1.Image = Image.FromFile(directory + "black_star.png");
            this.button2.Image = Image.FromFile(directory + "white_star.png");
            this.button3.Image = Image.FromFile(directory + "white_star.png");
            this.button4.Image = Image.FromFile(directory + "white_star.png");
            this.button5.Image = Image.FromFile(directory + "white_star.png");
        }

        private void button5_Click(object sender, EventArgs e)
        {
            counter = 5;
            this.button1.Image = Image.FromFile(directory + "black_star.png");
            this.button2.Image = Image.FromFile(directory + "black_star.png");
            this.button3.Image = Image.FromFile(directory + "black_star.png");
            this.button4.Image = Image.FromFile(directory + "black_star.png");
            this.button5.Image = Image.FromFile(directory + "black_star.png");
        }

        private void button2_Click(object sender, EventArgs e)
        {
            counter = 2;
            this.button1.Image = Image.FromFile(directory + "black_star.png");
            this.button2.Image = Image.FromFile(directory + "black_star.png");
            this.button3.Image = Image.FromFile(directory + "white_star.png");
            this.button4.Image = Image.FromFile(directory + "white_star.png");
            this.button5.Image = Image.FromFile(directory + "white_star.png");
        }

        private void button3_Click(object sender, EventArgs e)
        {
            counter = 3;
            this.button1.Image = Image.FromFile(directory + "black_star.png");
            this.button2.Image = Image.FromFile(directory + "black_star.png");
            this.button3.Image = Image.FromFile(directory + "black_star.png");
            this.button4.Image = Image.FromFile(directory + "white_star.png");
            this.button5.Image = Image.FromFile(directory + "white_star.png");
        }

        private void button4_Click(object sender, EventArgs e)
        {
            counter = 4;
            this.button1.Image = Image.FromFile(directory + "black_star.png");
            this.button2.Image = Image.FromFile(directory + "black_star.png");
            this.button3.Image = Image.FromFile(directory + "black_star.png");
            this.button4.Image = Image.FromFile(directory + "black_star.png");
            this.button5.Image = Image.FromFile(directory + "white_star.png");
        }

        private void button6_Click(object sender, EventArgs e)
        {
            if (counter != 0)
            {
                SingleConnection.send(counter.ToString());
                this.Hide();
                Select_Video_Form f1 = new Select_Video_Form();
                f1.ShowDialog();
            }
            else
            {
                MessageBox.Show("You must rate the video");
            }
        }
    }
}
