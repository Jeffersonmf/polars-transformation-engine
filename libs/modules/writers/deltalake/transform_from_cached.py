import asyncio
import json

from pydantic import TypeAdapter

from libs.modules.writers.deltalake.write_to_delta import PolarsTooling
from libs.repository.database.memory import Memory
from libs.triggers.mellishops import Mellishops
from libs.triggers.vtex import Vtex


class WriterToLandingZone(object):
    async def process_all_connectors(self):
        await asyncio.sleep(1)

        # colocar isso num Init da vida....
        redis = Memory()
        polars_tooling = PolarsTooling()

        # chamar aqui num while... infinito..
        rows_to_write = self.convert_to_typed_connectors(redis.load_connectors())

        IsOperationSuccess = polars_tooling.append_to_deltalake(rows_to_write)

        if IsOperationSuccess:
            # Remove from Redis...
            print(True)

    def convert_to_typed_connectors(self, connectors_list) -> list:
        typed_list = []

        for item in connectors_list:
            self.current_row = item
            try:
                self.trigger_name = json.loads(item)["trigger_name"]

                json_dict = json.loads(item)
                self.typed_obj: object

                if json_dict["trigger_name"] == "Mellishops":
                    self.typed_obj = TypeAdapter(Mellishops)
                elif json_dict["trigger_name"] == "Vtex":
                    self.typed_obj = TypeAdapter(Vtex)

                m = self.typed_obj.validate_python(json_dict)
                print(m)
                typed_list.append(m)

            except Exception as e:
                print(e)

        return typed_list
