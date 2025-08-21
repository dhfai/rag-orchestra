import sys
from typing import Optional, Tuple
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.markdown import Markdown
from ..core.models import UserInput, LLMModel, ValidationResult
from ..utils.logger import get_logger

logger = get_logger("UserInterface")
console = Console()

class UserInterface:
    """Interactive user interface for the RAG system"""

    def __init__(self):
        self.console = console

    def welcome_banner(self):
        """Display welcome banner"""
        banner_text = """
# 🎓 RAG Multi-Strategy System
## Sistem Pembuat Modul Ajar Kurikulum Merdeka

Selamat datang di sistem pembuat modul ajar yang menggunakan teknologi RAG (Retrieval-Augmented Generation)
dengan multiple strategy untuk menghasilkan modul pembelajaran berkualitas tinggi.
        """

        panel = Panel(
            Markdown(banner_text),
            title="[bold blue]Selamat Datang[/bold blue]",
            border_style="blue",
            padding=(1, 2)
        )
        self.console.print(panel)
        self.console.print()

    def collect_user_input(self) -> UserInput:
        """Collect user input interactively"""
        logger.step("Input Collection", "Mengumpulkan data dari pengguna")

        self.console.print("[bold cyan]📝 Silakan masukkan informasi berikut:[/bold cyan]")
        self.console.print()

        # Collect basic information
        nama_guru = Prompt.ask("[green]Nama Guru[/green]")
        nama_sekolah = Prompt.ask("[green]Nama Sekolah[/green]")
        mata_pelajaran = Prompt.ask("[green]Mata Pelajaran[/green]")
        topik = Prompt.ask("[green]Topik[/green]")
        sub_topik = Prompt.ask("[green]Sub Topik[/green]")
        kelas = Prompt.ask("[green]Kelas[/green]")
        alokasi_waktu = Prompt.ask("[green]Alokasi Waktu (contoh: 2 x 45 menit)[/green]")

        # Select LLM Model
        self.console.print("\n[bold cyan]🤖 Pilih Model LLM:[/bold cyan]")
        llm_choices = {
            "1": LLMModel.GEMINI_1_5_FLASH,
            "2": LLMModel.GPT_4
        }

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("No", style="dim", width=6)
        table.add_column("Model LLM", style="cyan")
        table.add_column("Deskripsi", style="dim")

        table.add_row("1", "Gemini 1.5 Flash", "Google AI - Cepat dan efisien")
        table.add_row("2", "GPT-4", "OpenAI - Powerful dan detail")

        self.console.print(table)

        model_choice = Prompt.ask(
            "[green]Pilihan Model LLM[/green]",
            choices=["1", "2"],
            default="1"
        )
        model_llm = llm_choices[model_choice]

        # Ask for CP and ATP
        self.console.print("\n[bold cyan]📚 CP dan ATP (Opsional):[/bold cyan]")
        has_cp_atp = Confirm.ask("[yellow]Apakah Anda sudah memiliki CP dan ATP?[/yellow]", default=False)

        cp = None
        atp = None

        if has_cp_atp:
            self.console.print("[dim]Silakan masukkan CP dan ATP Anda (tekan Enter dua kali untuk selesai):[/dim]")
            cp = self._multiline_input("CP (Capaian Pembelajaran)")
            atp = self._multiline_input("ATP (Alur Tujuan Pembelajaran)")

        user_input = UserInput(
            nama_guru=nama_guru,
            nama_sekolah=nama_sekolah,
            mata_pelajaran=mata_pelajaran,
            topik=topik,
            sub_topik=sub_topik,
            kelas=kelas,
            alokasi_waktu=alokasi_waktu,
            model_llm=model_llm,
            cp=cp,
            atp=atp
        )

        logger.user_interaction(f"Input collected: {mata_pelajaran} - {topik} - Kelas {kelas}")
        return user_input

    def _multiline_input(self, prompt_text: str) -> str:
        """Get multiline input from user"""
        self.console.print(f"[bold]{prompt_text}:[/bold]")
        self.console.print("[dim](Ketik teks Anda, tekan Enter dua kali untuk selesai)[/dim]")

        lines = []
        empty_line_count = 0

        while True:
            try:
                line = input()
                if line.strip() == "":
                    empty_line_count += 1
                    if empty_line_count >= 2:
                        break
                else:
                    empty_line_count = 0
                lines.append(line)
            except KeyboardInterrupt:
                self.console.print("\n[red]Input dibatalkan oleh user[/red]")
                return ""

        return "\n".join(lines).strip()

    def display_input_summary(self, user_input: UserInput):
        """Display summary of collected input"""
        logger.step("Input Summary", "Menampilkan ringkasan input")

        table = Table(title="📋 Ringkasan Input", show_header=False, border_style="green")
        table.add_column("Field", style="bold cyan", width=20)
        table.add_column("Value", style="white")

        table.add_row("Nama Guru", user_input.nama_guru)
        table.add_row("Nama Sekolah", user_input.nama_sekolah)
        table.add_row("Mata Pelajaran", user_input.mata_pelajaran)
        table.add_row("Topik", user_input.topik)
        table.add_row("Sub Topik", user_input.sub_topik)
        table.add_row("Kelas", user_input.kelas)
        table.add_row("Alokasi Waktu", user_input.alokasi_waktu)
        table.add_row("Model LLM", user_input.model_llm.value)
        table.add_row("CP Tersedia", "✅ Ya" if user_input.cp else "❌ Tidak")
        table.add_row("ATP Tersedia", "✅ Ya" if user_input.atp else "❌ Tidak")

        self.console.print(table)
        self.console.print()

    def show_cp_atp_generation_progress(self):
        """Show progress for CP/ATP generation"""
        logger.progress_start("Generating CP dan ATP")

        steps = [
            "Menganalisis kompleksitas tugas",
            "Memilih strategi RAG yang tepat",
            "Melakukan pencarian dokumen",
            "Memproses dengan LLM",
            "Validasi hasil"
        ]

        for i, step in enumerate(steps, 1):
            self.console.print(f"[cyan]⏳ Step {i}/5: {step}[/cyan]")

    def display_generated_cp_atp(self, cp_content: str, atp_content: str):
        """Display generated CP and ATP"""
        logger.step("CP/ATP Display", "Menampilkan hasil generasi CP dan ATP")

        # Display CP
        cp_panel = Panel(
            cp_content,
            title="[bold green]📚 Capaian Pembelajaran (CP)[/bold green]",
            border_style="green",
            padding=(1, 2)
        )
        self.console.print(cp_panel)
        self.console.print()

        # Display ATP
        atp_panel = Panel(
            atp_content,
            title="[bold blue]🎯 Alur Tujuan Pembelajaran (ATP)[/bold blue]",
            border_style="blue",
            padding=(1, 2)
        )
        self.console.print(atp_panel)
        self.console.print()

    def get_user_validation(self) -> ValidationResult:
        """Get user validation for generated CP/ATP"""
        logger.step("User Validation", "Meminta validasi dari pengguna")

        self.console.print("[bold yellow]🤔 Validasi CP dan ATP[/bold yellow]")

        is_approved = Confirm.ask(
            "[green]Apakah Anda setuju dengan CP dan ATP yang dihasilkan?[/green]",
            default=True
        )

        feedback = None
        requested_changes = []

        if not is_approved:
            self.console.print("[yellow]💭 Silakan berikan feedback untuk perbaikan:[/yellow]")
            feedback = self._multiline_input("Feedback Anda")

            # Ask for specific changes
            self.console.print("\n[yellow]🔧 Perubahan yang diinginkan (opsional):[/yellow]")
            self.console.print("[dim]Ketik setiap perubahan pada baris terpisah, Enter dua kali untuk selesai[/dim]")

            while True:
                change = input("- ")
                if change.strip() == "":
                    break
                requested_changes.append(change.strip())

        validation_result = ValidationResult(
            is_approved=is_approved,
            feedback=feedback,
            requested_changes=requested_changes if requested_changes else None
        )

        logger.user_interaction(f"Validation result: {'Approved' if is_approved else 'Rejected with feedback'}")
        return validation_result

    def show_refinement_progress(self):
        """Show progress for refinement process"""
        logger.progress_start("Melakukan refinement berdasarkan feedback")

        steps = [
            "Menganalisis feedback pengguna",
            "Menyesuaikan strategi RAG",
            "Mencari dokumen tambahan",
            "Regenerasi dengan perbaikan",
            "Validasi ulang"
        ]

        for i, step in enumerate(steps, 1):
            self.console.print(f"[yellow]🔄 Refinement {i}/5: {step}[/yellow]")

    def display_final_input(self, final_input):
        """Display final processed input"""
        logger.step("Final Input Display", "Menampilkan input final")

        self.console.print()
        self.console.rule("[bold green]🎉 FINAL INPUT - SIAP UNTUK TAHAP SELANJUTNYA[/bold green]")
        self.console.print()

        # Summary table
        summary_table = Table(title="📋 Final Input Summary", show_header=False, border_style="green")
        summary_table.add_column("Field", style="bold cyan", width=20)
        summary_table.add_column("Value", style="white")

        summary_table.add_row("Nama Guru", final_input.user_input.nama_guru)
        summary_table.add_row("Mata Pelajaran", final_input.user_input.mata_pelajaran)
        summary_table.add_row("Topik", final_input.user_input.topik)
        summary_table.add_row("Kelas", final_input.user_input.kelas)
        summary_table.add_row("Model LLM", final_input.user_input.model_llm.value)
        summary_table.add_row("Status CP/ATP", "✅ Validated")

        self.console.print(summary_table)
        self.console.print()

        # CP Content
        cp_panel = Panel(
            final_input.cp_content[:500] + "..." if len(final_input.cp_content) > 500 else final_input.cp_content,
            title="[bold green]📚 Final CP[/bold green]",
            border_style="green"
        )
        self.console.print(cp_panel)
        self.console.print()

        # ATP Content
        atp_panel = Panel(
            final_input.atp_content[:500] + "..." if len(final_input.atp_content) > 500 else final_input.atp_content,
            title="[bold blue]🎯 Final ATP[/bold blue]",
            border_style="blue"
        )
        self.console.print(atp_panel)
        self.console.print()

        # Processing metadata
        metadata_text = ""
        for key, value in final_input.processing_metadata.items():
            metadata_text += f"• {key}: {value}\n"

        metadata_panel = Panel(
            metadata_text,
            title="[bold yellow]⚙️ Processing Metadata[/bold yellow]",
            border_style="yellow"
        )
        self.console.print(metadata_panel)

        logger.success("Final input berhasil diproses dan siap untuk tahap selanjutnya!")

    def show_error(self, error_message: str):
        """Display error message"""
        error_panel = Panel(
            f"❌ {error_message}",
            title="[bold red]Error[/bold red]",
            border_style="red"
        )
        self.console.print(error_panel)
        logger.error(error_message)

    def show_warning(self, warning_message: str):
        """Display warning message"""
        warning_panel = Panel(
            f"⚠️ {warning_message}",
            title="[bold yellow]Warning[/bold yellow]",
            border_style="yellow"
        )
        self.console.print(warning_panel)
        logger.warning(warning_message)

    def confirm_exit(self) -> bool:
        """Confirm if user wants to exit"""
        return Confirm.ask("[red]Apakah Anda yakin ingin keluar?[/red]", default=False)
