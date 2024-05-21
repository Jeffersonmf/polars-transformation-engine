import asyncio
import sys

from libs.modules.consumers.triggers_reader import TriggersReader
from libs.modules.writers.deltalake.transform_from_cached import WriterToLandingZone

if __name__ == "__main__":
    args = sys.argv

    loop = asyncio.get_event_loop()

    def loader():
        starter_point = TriggersReader()
        loop.run_until_complete(starter_point.start_all_triggers())

    def writer():
        starter_point = WriterToLandingZone()
        loop.run_until_complete(starter_point.process_all_connectors())

    def invalid_option() -> str:
        print(
            "Invalid arguments.... You need to inform [loader] or [writer] as argument."
        )

    if len(args) > 1:
        command_argument = args[1]

        switch = {"loader": loader, "writer": writer}

        invalid = invalid_option

        selected_case = switch.get(command_argument, invalid)
        selected_case()

    else:
        invalid_option()
