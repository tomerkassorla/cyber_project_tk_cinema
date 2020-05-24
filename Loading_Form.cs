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
    public partial class Loading_Form : Form
    {
        public Action Worker { get; set; }
        public Loading_Form(Action worker)
        {
            InitializeComponent();
            this.StartPosition = FormStartPosition.CenterScreen;
            this.ControlBox = false;
            this.progressBar1.Style = ProgressBarStyle.Marquee;
            this.label1.Text = "Loading...";
            if (worker == null)
                throw new ArgumentNullException();
            Worker = worker;
        }
        protected override void OnLoad(EventArgs e)
        {
            base.OnLoad(e);
            Task.Factory.StartNew(Worker).ContinueWith(t => { this.Close(); }, TaskScheduler.FromCurrentSynchronizationContext());

        }
        private void loading_form_Load(object sender, EventArgs e)
        {
        }

        private void label1_Click(object sender, EventArgs e)
        {

        }
    }
}
