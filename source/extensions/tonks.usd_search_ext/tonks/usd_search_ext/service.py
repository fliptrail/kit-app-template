# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

from pathlib import Path
from pydantic import BaseModel, Field

import omni.kit.commands
import omni.usd
import omni.simready.explorer as simready_explorer
from omni.services.core.routers import ServiceAPIRouter

router = ServiceAPIRouter(tags=["Tonks USD Search Extension"])


class USDSearchQuery(BaseModel):
    text: str


@router.get(
    "/search",
    summary="Search for USD assets",
    description="An endpoint to search for USD assets",
)
async def search_usd(q: str):
    print("[tonks.usd_search_ext] search_usd was called with query: ", q)

    query = q.split(",")

    assets = await simready_explorer.find_assets(query)

    return assets
