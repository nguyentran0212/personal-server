import typer

app = typer.Typer(help="Servercraft CLI: scaffold Docker stacks with apps & foundations")

@app.command()
def init(stack_name: str):
    """
    Initialize a new Docker stack named STACK_NAME.
    """
    typer.echo(f"Initializing stack: {stack_name}")
    # TODO: implement scaffold logic per plan

def main():
    app()

if __name__ == "__main__":
    main()
