import logging
import math
from typing import Any, Callable, List, Optional, Tuple

import numpy as np
from OpenGL.GL import (GL_ARRAY_BUFFER, GL_FALSE, GL_FLOAT,
                       GL_MAX_SHADER_STORAGE_BLOCK_SIZE,
                       GL_MAX_SHADER_STORAGE_BUFFER_BINDINGS, GL_RGBA,
                       GL_RGBA32F, GL_SHADER_STORAGE_BUFFER, GL_STATIC_DRAW,
                       ctypes, glBindBuffer, glBindBufferBase,
                       glBindVertexArray, glBufferData, glClearBufferData,
                       glDeleteBuffers, glEnableVertexAttribArray,
                       glGenBuffers, glGetBufferSubData, glGetIntegerv,
                       glVertexAttribDivisor, glVertexAttribPointer)


def get_buffer_object_size(num_classes: int, additional_data: int) -> int:
    object_size: int = (4 - ((num_classes + additional_data) %
                        4)) % 4 + (num_classes + additional_data)
    return object_size


def get_buffer_padding(num_classes: int, additional_data: int) -> int:
    object_size: int = get_buffer_object_size(num_classes, additional_data)
    return object_size - (num_classes + additional_data)


def get_buffer_settings(num_classes: int, additional_data: int) -> Tuple[int, List[int], List[int]]:
    object_size: int = get_buffer_object_size(num_classes, additional_data)
    data_offset: List[int] = [i for i in range(0, object_size, 4)]
    data_size: List[int] = [4 for _ in range(int(object_size / 4))]
    return object_size, data_offset, data_size


class BufferObject:
    def __init__(self, ssbo: bool = False, object_size: int = 4, render_data_offset: Optional[List[int]] = None,
                 render_data_size: Optional[List[int]] = None) -> None:
        self.handle: int = glGenBuffers(1)
        self.location: int = 0
        self.ssbo: bool = ssbo
        if self.ssbo:
            self.size: int = 0
            self.max_ssbo_size: int = glGetIntegerv(
                GL_MAX_SHADER_STORAGE_BLOCK_SIZE)
        self.object_size: int = object_size
        self.render_data_offset: List[int] = [
            0] if render_data_offset is None else render_data_offset
        self.render_data_size: List[int] = [
            4] if render_data_size is None else render_data_size

    def load(self, data: Any) -> None:
        glBindVertexArray(0)

        self.size = data.nbytes
        if self.ssbo:
            if data.nbytes > self.max_ssbo_size:
                raise Exception('Data to big for SSBO (%d bytes, max %d bytes).' % (
                    data.nbytes, self.max_ssbo_size))

            glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.handle)
            glBufferData(GL_SHADER_STORAGE_BUFFER,
                         data.nbytes, data, GL_STATIC_DRAW)
        else:
            glBindBuffer(GL_ARRAY_BUFFER, self.handle)
            glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)

    def read(self) -> Any:
        if self.ssbo:
            glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.handle)
            return glGetBufferSubData(GL_SHADER_STORAGE_BUFFER, 0, self.size)

    def bind(self, location: int, rendering: bool = False, divisor: int = 0) -> None:
        if self.ssbo:
            if rendering:
                glBindBuffer(GL_ARRAY_BUFFER, self.handle)
                for i in range(len(self.render_data_offset)):
                    glEnableVertexAttribArray(location + i)
                    glVertexAttribPointer(location + i, self.render_data_size[i], GL_FLOAT, GL_FALSE,
                                          self.object_size * 4, ctypes.c_void_p(4 * self.render_data_offset[i]))
                    if divisor > 0:
                        glVertexAttribDivisor(location + i, divisor)
            else:
                glBindBufferBase(GL_SHADER_STORAGE_BUFFER,
                                 location, self.handle)
        else:
            glBindBuffer(GL_ARRAY_BUFFER, self.handle)
            for i in range(len(self.render_data_offset)):
                glEnableVertexAttribArray(location + i)
                glVertexAttribPointer(location + i, self.render_data_size[i], GL_FLOAT, GL_FALSE,
                                      self.object_size * 4, ctypes.c_void_p(4 * self.render_data_offset[i]))
                if divisor > 0:
                    glVertexAttribDivisor(location + i, divisor)

    def clear(self) -> None:
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 0, self.handle)
        glClearBufferData(GL_SHADER_STORAGE_BUFFER,
                          GL_RGBA32F, GL_RGBA, GL_FLOAT, None)

    def delete(self) -> None:
        glDeleteBuffers(1, [self.handle])


class SwappingBufferObject(BufferObject):
    def __init__(self, ssbo: bool = False, object_size: int = 4, render_data_offset: Optional[List[int]] = None,
                 render_data_size: Optional[List[int]] = None) -> None:
        super().__init__(ssbo, object_size, render_data_offset, render_data_size)
        self.swap_handle: int = glGenBuffers(1)

    def swap(self) -> None:
        self.handle, self.swap_handle = self.swap_handle, self.handle

    def bind(self, location: int, rendering: bool = False, divisor: int = 0) -> None:
        if self.ssbo:
            if rendering:
                glBindBuffer(GL_ARRAY_BUFFER, self.handle)
                for i in range(len(self.render_data_offset)):
                    glEnableVertexAttribArray(location + i)
                    glVertexAttribPointer(location + i, self.render_data_size[i], GL_FLOAT, GL_FALSE,
                                          self.object_size * 4, ctypes.c_void_p(4 * self.render_data_offset[i]))
                    if divisor > 0:
                        glVertexAttribDivisor(location + i, divisor)
            else:
                glBindBufferBase(GL_SHADER_STORAGE_BUFFER,
                                 location, self.handle)
                glBindBufferBase(GL_SHADER_STORAGE_BUFFER,
                                 location + 1, self.swap_handle)
        else:
            glBindBuffer(GL_ARRAY_BUFFER, self.handle)
            for i in range(len(self.render_data_offset)):
                glEnableVertexAttribArray(location + i)
                glVertexAttribPointer(location + i, self.render_data_size[i], GL_FLOAT, GL_FALSE,
                                      self.object_size * 4, ctypes.c_void_p(4 * self.render_data_offset[i]))
                if divisor > 0:
                    glVertexAttribDivisor(location + i, divisor)

    def delete(self) -> None:
        glDeleteBuffers(1, [self.handle])
        glDeleteBuffers(1, [self.swap_handle])


class OverflowingBufferObject:
    def __init__(self, data_splitting_function: Callable, object_size: int = 4, render_data_offset: Optional[List[int]] = None,
                 render_data_size: Optional[List[int]] = None) -> None:
        self.handle: List[int] = [glGenBuffers(1)]
        self.location: int = 0
        self.overall_size: int = 0
        self.size: List[int] = []
        self.max_ssbo_size: int = glGetIntegerv(
            GL_MAX_SHADER_STORAGE_BLOCK_SIZE)
        self.max_buffer_objects: int = glGetIntegerv(
            GL_MAX_SHADER_STORAGE_BUFFER_BINDINGS)
        self.data_splitting_function: Callable = data_splitting_function
        self.object_size: int = object_size
        self.render_data_offset: List[int] = [
            0] if render_data_offset is None else render_data_offset
        self.render_data_size: List[int] = [
            4] if render_data_size is None else render_data_size

    def load(self, data: Any) -> None:
        glBindVertexArray(0)

        self.overall_size = data.nbytes
        if data.nbytes > self.max_ssbo_size:
            buffer_count = math.ceil(data.nbytes / self.max_ssbo_size)
            for i in range(buffer_count):
                if i >= len(self.handle):
                    self.handle.append(glGenBuffers(1))
                glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.handle[i])
                split_data = self.data_splitting_function(
                    data, i, self.max_ssbo_size)
                self.size.append(split_data.nbytes)
                glBufferData(GL_SHADER_STORAGE_BUFFER,
                             split_data.nbytes, split_data, GL_STATIC_DRAW)
        else:
            self.size[0] = data.nbytes
            glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.handle[0])
            glBufferData(GL_SHADER_STORAGE_BUFFER,
                         data.nbytes, data, GL_STATIC_DRAW)

    def load_empty(self, dtype: Any, size: int, component_size: int) -> None:
        glBindVertexArray(0)

        self.overall_size = size * self.object_size * 4
        if self.overall_size > self.max_ssbo_size:
            empty = np.zeros(int(self.max_ssbo_size / 4), dtype=dtype)
            buffer_count = math.ceil(
                int(size / component_size) / int(self.max_ssbo_size / (component_size * self.object_size * 4)))
            logging.info('Data split into %i buffer' % buffer_count)
            for i in range(buffer_count):
                if i >= len(self.handle):
                    self.handle.append(glGenBuffers(1))
                glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.handle[i])
                self.size.append(empty.nbytes)
                glBufferData(GL_SHADER_STORAGE_BUFFER,
                             empty.nbytes, empty, GL_STATIC_DRAW)
        else:
            empty = np.zeros(size * self.object_size, dtype=dtype)
            self.size.append(empty.nbytes)
            glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.handle[0])
            glBufferData(GL_SHADER_STORAGE_BUFFER,
                         empty.nbytes, empty, GL_STATIC_DRAW)

    def read(self) -> Any:
        data: Optional[Any] = None
        for i, buffer in enumerate(self.handle):
            glBindBuffer(GL_SHADER_STORAGE_BUFFER, buffer)
            if data is None:
                data = glGetBufferSubData(
                    GL_SHADER_STORAGE_BUFFER, 0, self.size[i])
            else:
                data.extend(glGetBufferSubData(
                    GL_SHADER_STORAGE_BUFFER, 0, self.size[i]))
        return data

    def bind_single(self, buffer_id: int, location: int, rendering: bool = False, divisor: int = 0) -> None:
        if rendering:
            glBindBuffer(GL_ARRAY_BUFFER, self.handle[buffer_id])
            for i in range(len(self.render_data_offset)):
                glEnableVertexAttribArray(location + i)
                glVertexAttribPointer(location + i, self.render_data_size[i], GL_FLOAT, GL_FALSE,
                                      self.object_size * 4, ctypes.c_void_p(4 * self.render_data_offset[i]))
                if divisor > 0:
                    glVertexAttribDivisor(location + i, divisor)
        else:
            glBindBufferBase(GL_SHADER_STORAGE_BUFFER,
                             location, self.handle[buffer_id])

    def bind_consecutive(self, location: int) -> None:
        for i, buffer in enumerate(self.handle):
            glBindBufferBase(GL_SHADER_STORAGE_BUFFER,
                             location + i, len(self.handle), buffer)

    def clear(self) -> None:
        for buffer in self.handle:
            glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 0, buffer)
            glClearBufferData(GL_SHADER_STORAGE_BUFFER,
                              GL_RGBA32F, GL_RGBA, GL_FLOAT, None)

    def delete(self) -> None:
        for buffer in self.handle:
            glDeleteBuffers(1, [buffer])
        self.handle = []

    def get_objects(self, buffer_id: int = 0) -> int:
        return int(self.size[buffer_id] / (self.object_size * 4))
