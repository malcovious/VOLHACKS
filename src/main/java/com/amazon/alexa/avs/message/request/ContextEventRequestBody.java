/**
 * Copyright 2015 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *
 * You may not use this file except in compliance with the License. A copy of the License is located the "LICENSE.txt"
 * file accompanying this source. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied. See the License for the specific language governing permissions and limitations
 * under the License.
 */

package com.amazon.alexa.avs.message.request;

import com.amazon.alexa.avs.message.request.context.ComponentState;

import java.util.List;

public class ContextEventRequestBody extends RequestBody {

    private final List<ComponentState> context;

    public ContextEventRequestBody(List<ComponentState> context, Event event) {
        super(event);
        this.context = context;
    }

    public final List<ComponentState> getContext() {
        return context;
    }

}