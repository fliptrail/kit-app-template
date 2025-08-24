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

import omni.simready.explorer as simready_explorer
from omni.services.core.routers import ServiceAPIRouter
from .simple_zinc_client import SimpleZincClient

router = ServiceAPIRouter(tags=["Tonks USD Search Extension"])
zinc_client = SimpleZincClient(url="http://zincsearch:4080", username="admin", password="Complexpass#123")

class USDSearchQuery(BaseModel):
    text: str


@router.get(
    "/search",
    summary="Search for USD assets",
    description="Search USD assets using simready_explorer first, then ZincSearch as fallback",
)
async def search_usd(q: str):
    print(f"[tonks.usd_search_ext] search_usd called with query: {q}")

    # First try simready_explorer
    print("[tonks.usd_search_ext] Trying simready_explorer first")
    query = q.split(",")
    assets = await simready_explorer.find_assets(query)

    # If we got results, return them
    if assets and len(assets) > 0:
        print(f"[tonks.usd_search_ext] simready_explorer returned {len(assets)} results")
        return assets

    # If no results, try ZincSearch as fallback
    print("[tonks.usd_search_ext] No results from simready_explorer, trying ZincSearch")

    if zinc_client:
        try:
            zinc_results = await zinc_client.search(q)
            if zinc_results:
                print(f"[tonks.usd_search_ext] ZincSearch returned {len(zinc_results)} results")
                return zinc_results
        except Exception as e:
            print(f"[tonks.usd_search_ext] ZincSearch error: {e}")

    print("[tonks.usd_search_ext] No results found")
    return []
