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
    public partial class Login_Form : Form
    {
        private string directory = "";
        public Login_Form()
        {
            InitializeComponent();
            project_path path = new project_path();
            this.directory = path.get_project_path();
            this.BackgroundImage = Image.FromFile(directory + "login.PNG");  
        }
        private void button1_Click(object sender, EventArgs e)
        {
            string username = textBox1.Text;
            string password = textBox2.Text;
            SingleConnection.send(username + "<%>" + password);
            string message = SingleConnection.recv();
            if (message == "ok")
            {
                Select_Video_Form form1 = new Select_Video_Form();
                this.Hide();
                form1.ShowDialog();
            }
            else
            {
                MessageBox.Show(message);
            }
        }

        private void button2_Click(object sender, EventArgs e)
        {
            string username = textBox1.Text;
            string password = textBox2.Text;
            SingleConnection.send(username + "<&>" + password);
            string message = SingleConnection.recv();
            if (message == "ok")
            {
                Select_Video_Form form1 = new Select_Video_Form();
                this.Hide();
                form1.ShowDialog();
            }
            else
            {
                MessageBox.Show(message);
            }
        }
        private void ButtonsForm_FormClosing(object sender, FormClosingEventArgs e)
        {
            SingleConnection.StopPythonEngine();
        }
        private void LoginForm_Load(object sender, EventArgs e)
        {
            SingleConnection.Connect();
        }

        private void textBox1_TextChanged(object sender, EventArgs e)
        {

        }

        private void label1_Click(object sender, EventArgs e)
        {

        }
    }
}
