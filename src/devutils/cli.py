
from pathlib import Path
import sys
import json
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from devutils.modules.qr import generate_qr, ascii_qr
from devutils.modules.ping import http_ping
from devutils.modules.base64util import b64_encode, b64_decode
from devutils.modules.duplicates import find_duplicates

app = typer.Typer(add_completion=False, no_args_is_help=True, help="DevUtils CLI")
console = Console()


@app.command()
def qr(
    text: str = typer.Option(None, "--text", "-t", help="Текст для QR"),
    input_file: Path = typer.Option(None, "--in", help="Файл с текстом"),
    output: Path = typer.Option(Path("qr.png"), "--out", "-o", help="PNG файл"),
    size: int = typer.Option(6, help="Размер модуля"),
    border: int = typer.Option(4, help="Рамка"),
    preview: bool = typer.Option(False, "--preview", help="Показать ASCII превью"),
):
    if not text and not input_file:
        raise typer.BadParameter("Укажите --text или --in")
    if input_file:
        text = input_file.read_text(encoding="utf-8")
    path = generate_qr(text, output, box_size=size, border=border)
    if preview:
        console.print(Panel.fit(ascii_qr(text), title="Preview"))
    console.print(f"[bold green]Saved:[/bold green] {path}")


@app.command()
def ping(
    url: str = typer.Argument(..., help="URL"),
    count: int = typer.Option(4, "-c", help="Количество запросов"),
    timeout: float = typer.Option(3.0, "-w", help="Таймаут, сек"),
    json_output: bool = typer.Option(False, "--json", help="Вывод JSON"),
):
    results = http_ping(url, count=count, timeout=timeout)
    if json_output:
        console.print_json(data=results)
        raise typer.Exit()

    table = Table(title="HTTP ping", box=box.SIMPLE)
    table.add_column("#")
    table.add_column("Status")
    table.add_column("Time, ms")
    for i, r in enumerate(results["samples"], 1):
        st = str(r.get("status", "-"))
        ms = f"{r.get('ms', 0):.1f}"
        color = "green" if r.get("ok") else "red"
        table.add_row(str(i), f"[{color}]{st}[/{color}]", ms)
    console.print(table)

    stats = results["stats"]
    panel = Panel.fit(
        f"sent={stats['sent']} received={stats['received']} loss={stats['loss']:.0%}\n"
        f"min={stats['min_ms']:.1f} avg={stats['avg_ms']:.1f} max={stats['max_ms']:.1f}",
        title="Summary",
    )
    console.print(panel)


@app.command("b64")
def b64(
    mode: str = typer.Argument(..., help="encode|decode"),
    input_path: Path = typer.Option(None, "--in", help="Входной файл"),
    output_path: Path = typer.Option(None, "--out", help="Выходной файл"),
    text: str = typer.Option(None, "--text", help="Текстовый ввод"),
):
    mode = mode.lower()
    if mode not in {"encode", "decode"}:
        raise typer.BadParameter("mode: encode|decode")

    data: bytes
    if input_path:
        data = input_path.read_bytes()
    elif text is not None:
        data = text.encode()
    else:
        data = sys.stdin.buffer.read()

    if mode == "encode":
        out = b64_encode(data)
    else:
        out = b64_decode(data)

    if output_path:
        output_path.write_bytes(out)
        console.print(f"[green]Saved:[/green] {output_path}")
    else:
        sys.stdout.buffer.write(out)


@app.command()
def dupes(
    path: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    min_size: int = typer.Option(1, help="Мин. размер файла, байт"),
    algo: str = typer.Option("md5", help="Хеш: md5|sha1|sha256"),
    delete: bool = typer.Option(False, help="Удалить дубли кроме первого"),
):
    groups = find_duplicates(path, min_size=min_size, algo=algo)
    if not groups:
        console.print("[green]Дубликаты не найдены[/green]")
        raise typer.Exit()

    table = Table(title="Дубликаты", box=box.SIMPLE_HEAVY)
    table.add_column("Группа")
    table.add_column("Размер")
    table.add_column("Файлы")

    for i, g in enumerate(groups, 1):
        size = g[0][1]
        files = "\\n".join(str(p) for p, _ in g)
        table.add_row(str(i), str(size), files)
    console.print(table)

    if delete:
        for g in groups:
            for p, _ in g[1:]:
                try:
                    p.unlink(missing_ok=True)
                except Exception:
                    pass
        console.print("[yellow]Дубли удалены[/yellow]")


if __name__ == "__main__":
    app()
